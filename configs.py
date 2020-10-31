# -*- coding: utf-8 -*-
import sqlite3


class QuestDB(sqlite3.Connection):
    def __init__(self):
        super(QuestDB, self).__init__('quests.db')
        self.cur = self.cursor()

    @property
    def quest_db(self):
        quests = self.cur.execute('select * from quests').fetchall()
        return quests

    @property
    def selected(self):
        quests = self.cur.execute('select * from quests where is_selected = 1').fetchall()
        return quests

    def set_selected(self, quest_id_list):
        print(quest_id_list)
        with self:
            for quest in quest_id_list:
                self.cur.execute('update quests SET is_selected = 1 where quest_id = ?', [quest])

    def set_unselected(self, quest_id_list):
        with self:
            for quest in quest_id_list:
                self.cur.execute('update quests SET is_selected = Null where quest_id = ?', [quest])

    def get_quest_by_id(self, quest_id):
        quest = self.cur.execute('select * from quests where quest_id = ?', [quest_id]).fetchone()
        return quest

    def get_categories(self):
        result = self.cur.execute('SELECT tab_name FROM quests').fetchall()
        result = set(result)
        return sorted([r[0] for r in result], key=lambda i: i.lower())

    def get_quests_by_category(self, category):
        result = self.cur.execute('select * from quests where tab_name = ? order by quest_name', (category,)).fetchall()
        return result

    def get_selected_ids(self):
        result = self.cur.execute('select quest_id from quests where is_selected = 1').fetchall()
        return [r[0] for r in result]


class Pointers(sqlite3.Connection):
    def __init__(self):
        super(Pointers, self).__init__('pointers.db')
        self.cur = self.cursor()

    def get_pointers(self, pointer_name):
        pointers = self.cur.execute('SELECT * from pointers where pointer_name = ?', [pointer_name]).fetchone()
        module = pointers[1]
        try:
            base_pointer = int(pointers[2], 16)
        except ValueError:
            base_pointer = ''

        _pointers = []
        for i in pointers[3::]:
            try:
                append_i = int(i, 16)
            except ValueError:
                append_i = ''
            _pointers.append(append_i)

        return module, base_pointer, _pointers

    def save_pointers(self, pointer_list, pointer_name):
        with self:
            query = '''
                UPDATE pointers
                SET module = ?, base_pointer = ?, pointer1 = ?, pointer2 = ?, pointer3 = ?, pointer4 = ?, pointer5 = ?,
                pointer6 = ?, pointer7 = ? WHERE pointer_name = ?
            '''
            self.cur.execute(query, pointer_list + [pointer_name])
