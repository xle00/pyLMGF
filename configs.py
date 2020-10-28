# -*- coding: utf-8 -*-
import sqlite3


class SqlConnector:
    def __init__(self):
        self.connector = sqlite3.connect('quests.db', check_same_thread=False)
        self.cursor = self.connector.cursor()


class QuestDB(SqlConnector):
    def __init__(self):
        super(QuestDB, self).__init__()

    @property
    def quest_db(self):
        quests = self.cursor.execute('select * from quests').fetchall()
        return quests

    @property
    def selected(self):
        quests = self.cursor.execute('select * from quests where is_selected = 1').fetchall()
        return quests

    def update_selected(self, quest_id_list):
        with self.connector:
            self.cursor.execute('UPDATE quests SET is_selected = Null')
            for quest in quest_id_list:
                self.cursor.execute('update quests SET is_selected = 1 where quest_id = ?', [quest])

    def get_quest_by_id(self, quest_id):
        quest = self.cursor.execute('select * from quests where quest_id = ?', [quest_id]).fetchone()
        return quest


class Pointers(SqlConnector):
    def __init__(self):
        super(Pointers, self).__init__()

    def get_pointers(self, pointer_name):
        pointers = self.cursor.execute('SELECT * from pointers where pointer_name = ?', [pointer_name]).fetchone()
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
        with self.connector:
            query = '''
                UPDATE pointers
                SET module = ?, base_pointer = ?, pointer1 = ?, pointer2 = ?, pointer3 = ?, pointer4 = ?, pointer5 = ?,
                pointer6 = ?, pointer7 = ? WHERE pointer_name = ?
            '''
            self.cursor.execute(query, pointer_list + [pointer_name])
