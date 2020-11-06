# -*- coding: utf-8 -*-
import sqlite3


class QuestDB(sqlite3.Connection):
    def __init__(self):
        super(QuestDB, self).__init__('quests.db')
        self.cur = self.cursor()

    def set_selected(self, quest_id_list):
        subquery = f"({','.join(['?'] * len(quest_id_list))})"
        with self:
            self.cur.execute(f'UPDATE quests2 SET selected = 1 WHERE id IN {subquery}', quest_id_list)

    def set_unselected(self, quest_id_list):
        subquery = f"({','.join(['?']*len(quest_id_list))})"
        with self:
            self.cur.execute(f'UPDATE quests2 SET selected = Null WHERE id IN {subquery}', quest_id_list)

    def get_quest_by_id(self, quest_id):
        quest = self.cur.execute('SELECT * FROM quests2 WHERE id = ?', (quest_id,)).fetchone()
        return quest

    def get_categories(self):
        result = self.cur.execute('SELECT category FROM quests2').fetchall()
        result = set(result)
        return sorted([r[0] for r in result], key=lambda i: i.lower())

    def get_quests_by_category(self, category):
        result = self.cur.execute('SELECT * FROM quests2 where category = ? ORDER BY name', (category,)).fetchall()
        return result

    def get_selected_ids(self):
        result = self.cur.execute('SELECT id FROM quests2 WHERE selected = 1').fetchall()
        return [r[0] for r in result]

    def identify_quest(self, points, req, time):
        result = self.cur.execute(
            'SELECT quest_id FROM quests2 WHERE points = ? AND req = ? AND time = ?',
            (points, req, time)).fetchone()
        return result[0]


class Pointers(sqlite3.Connection):
    def __init__(self):
        super(Pointers, self).__init__('pointers.db')
        self.cur = self.cursor()
        self.create_pointers_table()

    def create_pointers_table(self):
        with self:
            self.cur.execute('''CREATE TABLE IF NOT EXISTS pointers (
                    name TEXT,
                    module TEXT,
                    base_offset TEXT,
                    offsets TEXT
                )''')

    def get_pointers(self):
        result = self.cur.execute('select * from pointers').fetchall()
        formatted = []
        for r in result:
            name, module, base, offsets = r
            offsets = [int(offset, 16) for offset in offsets.split()]
            formatted.append([name, module, int(base, 16), *offsets])
        return formatted

    def get_pointer_by_name(self, name):
        result = self.cur.execute('SELECT * FROM pointers WHERE name = ?', (name,)).fetchone()
        module = result[1]
        base_offset = int(result[2], 16)
        offsets = [int(i, 16) for i in result[3].split()]
        return module, base_offset, offsets

    def save_pointers(self, name, values):
        with self:
            query = '''
                UPDATE pointers
                SET module = ?, base_offset = ?, offsets = ? WHERE name = ?
            '''
            self.cur.execute(query, (*values, name))


class HistoryDB(sqlite3.Connection):
    def __init__(self):
        super(HistoryDB, self).__init__('history.db')
        self.cur = self.cursor()
        self.create_indexes_table()
        self.create_history_table()

    def create_history_table(self):
        with self:
            self.cur.execute('''CREATE TABLE IF NOT EXISTS history (
                sid INTEGER,
                time INTEGER,
                identifier TEXT,
                slot INTEGER,
                value INTEGER
            )''')

    def create_indexes_table(self):
        with self:
            self.cur.execute('''CREATE TABLE IF NOT EXISTS indexes (
                sid INTEGER,
                name TEXT,
                start INTEGER,
                end INTEGER,
                selected STRING,
                found INTEGER
            )''')

    def get_highest_sid(self):
        result = self.cur.execute('SELECT sid FROM indexes order by sid DESC').fetchone()
        return -1 if not result else result[0]

    def insert_session(self, sid: int, name: str, start: int, end: int, selected: iter):
        selected = ','.join(selected)
        with self:
            self.cur.execute('INSERT INTO indexes VALUES (?, ?, ?, ?, ?, Null)', (sid, name, start, end, selected))

    def get_sessions(self):
        result = self.cur.execute('SELECT * FROM indexes').fetchall()
        return result

    def get_session_by_sid(self, sid):
        result = self.cur.execute('SELECT * FROM indexes where sid = ?', (sid,)).fetchone()
        return result

    def set_session_end(self, sid, timestamp):
        with self:
            self.cur.execute('UPDATE indexes SET end = ? where sid = ?', (timestamp, sid))

    def insert_history(self, sid: int, time: int, identifier: str, slot: int, value: int):
        with self:
            self.cur.execute('''INSERT INTO history VALUES (?, ?, ?, ?, ?)''', (sid, time, identifier, slot, value))

    def get_history_by_sid(self, sid):
        result = self.cur.execute('SELECT * FROM history where sid = ? order by rowid', (sid,)).fetchall()
        print(result)
        return result

    def get_last_identifier(self, sid, slot):
        result = self.cur.execute('SELECT identifier FROM history WHERE sid = ? AND SLOT = ? ORDER BY rowid DESC',
                                  (sid, slot)).fetchone()
        return result
