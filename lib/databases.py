# -*- coding: utf-8 -*-
import sqlite3
from lib.functions import get_system_language


class QuestDB(sqlite3.Connection):
    def __init__(self):
        super(QuestDB, self).__init__('data\\quests.db')
        self.cur = self.cursor()
        self.lang = get_system_language()[:2]
        self.game_lang = None

    def set_selected(self, quest_id_list):
        subquery = f"({','.join(['?'] * len(quest_id_list))})"
        with self:
            self.cur.execute(f'UPDATE quests2 SET selected = 1 WHERE id IN {subquery}', quest_id_list)

    def set_unselected(self, quest_id_list):
        subquery = f"({','.join(['?']*len(quest_id_list))})"
        with self:
            self.cur.execute(f'UPDATE quests2 SET selected = Null WHERE id IN {subquery}', quest_id_list)

    def get_quest_by_id(self, quest_id):
        quest = list(self.cur.execute('SELECT * FROM quests2 WHERE id = ?', (quest_id,)).fetchone())
        quest[1] = self.get_quest_name(quest[1])
        return quest

    def get_categories(self):
        try:
            result = self.cur.execute(f'SELECT {self.lang} FROM categories').fetchall()
        except sqlite3.OperationalError:
            result = self.cur.execute(f'SELECT en FROM categories').fetchall()
        return sorted([r[0] for r in result], key=lambda i: i.lower())

    def get_quests_by_category(self, category):
        cat = self.get_category_id(category)
        result = self.cur.execute('SELECT * FROM quests2 where category = ? ORDER BY name', (cat,)).fetchall()
        # print(result)
        new_result = []
        for items in result:
            items = list(items)
            name = self.get_quest_name(items[1])
            items[1] = name
            new_result.append(items)
        return new_result

    def get_quest_name(self, nid):
        try:
            result = self.cur.execute(f'SELECT {self.lang} FROM quest_names WHERE id = ?', (nid,)).fetchone()
        except sqlite3.OperationalError:
            result = self.cur.execute(f'SELECT en FROM quest_names WHERE id = ?', (nid,)).fetchone()

        return result[0]

    def get_quest_name_from_qid(self, qid):
        nid = self.cur.execute('SELECT NAME FROM quests2 WHERE id = ?', (qid,)).fetchone()
        if nid:
            return self.get_quest_name(nid[0])

    def get_category_id(self, category):
        try:
            result = self.cur.execute(f'SELECT id FROM categories where {self.lang} = ?', (category,)).fetchone()
        except sqlite3.OperationalError:
            result = self.cur.execute(f'SELECT id FROM categories where en = ?', (category,)).fetchone()
        return result[0]

    def get_selected_ids(self):
        result = self.cur.execute('SELECT id FROM quests2 WHERE selected = 1').fetchall()
        return [r[0] for r in result]

    def identify_quest(self, points, req, time, name=None):
        result = self.cur.execute(
            'SELECT id, ambig FROM quests2 WHERE points = ? AND req = ? AND time = ?',
            (points, req, time)).fetchall()
        if len(result) == 1:
            return result[0][0]
        else:
            return self.resolve_ambiguity(result, name)

    def resolve_ambiguity(self, quests: iter, name: str):
        name = name.lower()
        for qid, ambid in quests:
            # print(qid)
            partial = self.cur.execute(f'SELECT {self.game_lang} FROM ambigs WHERE id = ?', (ambid,)).fetchone()[0]
            if partial in name:
                return qid

    def get_ambig_langs(self):
        result = self.cur.execute('SELECT * FROM ambigs')
        return [i[0] for i in result.description if i != 'id']

    def get_quest_points(self, qid):
        if qid:
            return self.cur.execute('SELECT points FROM quests2 WHERE id = ?', (qid, )).fetchone()[0]


class HistoryDB(sqlite3.Connection):
    def __init__(self):
        super(HistoryDB, self).__init__('data\\history.db')
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
                selected STRING
            )''')

    def get_highest_sid(self):
        result = self.cur.execute('SELECT sid FROM indexes order by sid DESC').fetchone()
        return -1 if not result else result[0]

    def insert_session(self, sid: int, name: str, start: int, selected: iter):
        selected = ','.join([str(i) for i in selected])
        with self:
            self.cur.execute('INSERT INTO indexes VALUES (?, ?, ?, ?)', (sid, name, start, selected))

    def get_sessions(self):
        result = self.cur.execute('SELECT * FROM indexes').fetchall()
        return result

    def get_session_by_sid(self, sid):
        result = self.cur.execute('SELECT * FROM indexes where sid = ?', (sid,)).fetchone()
        return result

    def insert_history(self, sid: int, time: int, identifier: str, slot: int, value: int):
        with self:
            self.cur.execute('''INSERT INTO history VALUES (?, ?, ?, ?, ?)''', (sid, time, identifier, slot, value))

    def get_history_by_sid(self, sid):
        result = self.cur.execute('SELECT * FROM history where sid = ? order by time', (sid,)).fetchall()
        return result

    def get_last_identifier(self, sid, slot):
        result = self.cur.execute('SELECT identifier FROM history WHERE sid = ? AND SLOT = ? ORDER BY rowid DESC',
                                  (sid, slot)).fetchone()
        return result

    def get_last_for_session(self, sid):
        result = self.cur.execute('SELECT time, identifier, value'
                                  ' FROM history where sid = ? order by time DESC', (sid,)).fetchone()
        return result

    def delete_session(self, sid):
        with self:
            self.cur.execute('DELETE FROM indexes WHERE sid = ?', (sid,))
            self.cur.execute('DELETE FROM history WHERE SID = ?', (sid,))


class LocalDB(sqlite3.Connection):
    def __init__(self):
        super(LocalDB, self).__init__('data\\localization.db')
        self.cur = self.cursor()
        self.locale = get_system_language()

    def get_main_localization(self):
        try:
            result = self.cur.execute(f'SELECT id, {self.locale} FROM main').fetchall()
        except sqlite3.OperationalError:
            result = self.cur.execute(f'SELECT id, en_us FROM main').fetchall()
        return dict(i for i in result)
