# -*- coding: utf-8 -*-
import os
from time import strptime, sleep, perf_counter
from datetime import datetime

import win32api
import win32con
import win32gui

from mss import mss
from PIL import ImageGrab
from configs import QuestDB, Pointers
from pushbullet import PushBullet
from readprocessmemory import ProcessMemory

db = QuestDB()
pointers = Pointers()
sct = mss()


def get_time_now():
    dtime = datetime.now()
    year = f'{dtime:%Y}'
    month = f'{dtime:%m}'
    day = f'{dtime:%d}'
    hour = f'{dtime:%H}'
    minute = f'{dtime:%M}'
    second = f'{dtime:%S}'
    return f'{year} {month} {day} {hour} {minute} {second} '


def save_to_history(string):
    with open('history.txt', 'a') as f:
        f.write(string+'\n')


class LMReadMemory:
    def __init__(self):
        self.lm = ProcessMemory('Lords Mobile.exe')
        self.get_pointer = self.lm.get_pointer
        self.read_str = self.lm.read_string
        self.name = self.get_username

    def get_active_time(self):
        module, base_pointer, pointers_ = pointers.get_pointers('active_time')
        dll_base_address = self.lm.get_module_address_by_name(module)
        address = self.get_pointer(dll_base_address + base_pointer, pointers_)
        value = self.read_str(address, 5)
        time = strptime(value, '%M:%S').tm_sec + strptime(value, '%M:%S').tm_min * 60
        return time

    def get_mission_details(self):
        module, base_pointer, pointers_ = pointers.get_pointers('quest_points')
        dll_base_address = self.lm.get_module_address_by_name(module)
        quest_points_address = self.get_pointer(dll_base_address + base_pointer, pointers_)

        module, base_pointer, pointers_ = pointers.get_pointers('quest_requirements')
        dll_base_address = self.lm.get_module_address_by_name(module)
        quest_reqs_address = self.get_pointer(dll_base_address + base_pointer, pointers_)

        module, base_pointer, pointers_ = pointers.get_pointers('quest_time')
        dll_base_address = self.lm.get_module_address_by_name(module)
        quest_time_address = self.get_pointer(dll_base_address + base_pointer, pointers_)

        points = self.read_str(quest_points_address, 4)
        requirements = self.read_str(quest_reqs_address, 20)
        quest_time = self.read_str(quest_time_address, 11)

        result = {'Points': points[1::], 'Requirements': requirements[4::], 'Time': quest_time}

        return result

    @property
    def get_username(self):
        module, base_pointer, pointers_ = pointers.get_pointers('player_name')
        dll_base_address = self.lm.get_module_address_by_name(module)
        address = self.get_pointer(dll_base_address + base_pointer, pointers_)
        value = self.read_str(address, 12)
        username = ''
        for char in value:
            if ord(char) == 0:
                break
            username += char
        return username


class Mouse:
    @staticmethod
    def set_pos(x, y):
        win32api.SetCursorPos((x, y))

    @staticmethod
    def get_pos():
        return win32api.GetCursorPos()

    @staticmethod
    def wheel(clicks, x=None, y=None, interval=0.001):
        wheelturns = abs(clicks)
        if x and y:
            Mouse.set_pos(x, y)

        for _ in range(wheelturns):
            if clicks > 0:
                win32api.mouse_event(0x0800, 0, 0, -1, 0)
            elif clicks < 0:
                win32api.mouse_event(0x0800, 0, 0, 1, 0)
            sleep(interval)

    @staticmethod
    def left_click(x=None, y=None, lenght=0.005):
        if not x and not y:
            x, y = Mouse.get_pos()
        Mouse.set_pos(x, y)
        win32api.mouse_event(0x02, 0, 0, 0, 0)
        sleep(lenght)
        win32api.mouse_event(0x04, 0, 0, 0, 0)


class GuildFest(LMReadMemory):
    def __init__(self):
        super(GuildFest, self).__init__()
        self.x_coords = [294, 491, 661]
        self.y_coords = [456, 695, 676, 701, 694, 712, 710]
        self.selected = db.selected
        self.hwnd = win32gui.FindWindow('UnityWndClass', 'Lords Mobile')
        self.activate_window()
        sleep(.25)
        self.lm_pos = win32gui.GetWindowRect(self.hwnd)
        self.d_time = '0 0 0 0 0 0'
        self.start()

    def activate_window(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(self.hwnd)

    def get_the_mission(self, slot=None, text='', quest_id=None):
        self.lm_pos = win32gui.GetWindowRect(self.hwnd)
        if slot is not None:
            self.go_to_slot(slot)

        print(f'Pegando a Missão: {text}')
        Mouse.left_click(self.lm_pos[0] + 867, self.lm_pos[1] + 679)

        sleep(4)
        brightness = self.check_pixel_area_brightness((self.lm_pos[0] + 885, self.lm_pos[1] + 354, 1, 1))
        if brightness < 127:
            print('Erro ao pegar missão\n')
            return

        save_to_history(self.d_time + str(quest_id) + ' 1 ' + self.get_username)

        bbox = (self.lm_pos[0] + 764, self.lm_pos[1] + 329, self.lm_pos[0] + 1114, self.lm_pos[1] + 622)

        img = ImageGrab.grab(bbox=bbox)
        img.save('tempimage.jpeg')

        pb.push_img('tempimage.jpeg', title=f'Missão Pronta [{self.get_username}]', body=text)
        pb.push_img('tempimage.jpeg', email='thallesrafael1402@gmail.com',
                    title=f'Missão Pronta [{self.get_username}]', body=text)

        os.remove('tempimage.jpeg')

        exit()

    def get_quest_name(self):
        quest = self.get_mission_details()
        self.d_time = get_time_now()

        query_result = db.cursor.execute(
            'SELECT * from quests where quest_points = ? and quest_requirements = ? and quest_time = ?',
            (quest['Points'], quest['Requirements'], quest['Time'])).fetchone()

        if query_result:
            quest_id, quest_name, quest_points, _, _, is_selected, _, _ = query_result

            text = f'+{quest_points:<4} {quest_name}'
            if is_selected:
                # print(text, 'is selected')
                self.get_the_mission(text=text, quest_id=quest_id)
            save_to_history(self.d_time + str(quest_id) + ' 0 ' + self.get_username)
            return text
        else:
            save_to_history(self.d_time + '-1' + ' 0 ' + self.get_username)
            with db.connector:
                query = 'INSERT INTO quests VALUES ("","Unknown",?,?,?,"","Unknown","")'
                db.cursor.execute(query, (quest['Points'], quest['Requirements'], quest['Time']))

            self.lm_pos = win32gui.GetWindowRect(self.hwnd)
            bbox = (self.lm_pos.x + 764, self.lm_pos.y + 329, self.lm_pos.x + 1114, self.lm_pos.y + 622)

            img = ImageGrab.grab(bbox=bbox)
            img.save(f'{self.d_time}.jpg')

            return f'{quest} missão não identificada'

    def go_to_slot(self, slot):
        wheel_turns = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 7, 7: 7, 8: 7, 9: 14, 10: 14, 11: 14, 12: 21, 13: 21,
                       14: 21, 15: 28, 16: 28, 17: 28, 18: 35, 19: 35, 20: 35}
        self.activate_window()

        self.lm_pos = win32gui.GetWindowRect(self.hwnd)
        x, y = self.x_coords[slot % 3], self.y_coords[slot // 3]
        sleep(.1)

        if slot <= 5:
            Mouse.left_click(self.lm_pos[0] + x, self.lm_pos[1] + y)
            return
        else:
            Mouse.wheel(wheel_turns[slot], interval=.005)
            Mouse.left_click(self.lm_pos[0] + x, self.lm_pos[1] + y)
            Mouse.wheel(-wheel_turns[slot])
        sleep(.1)

    def get_sorted_time_list(self, board_times=None):
        if not board_times:
            board_times = self.get_board()

        if board_times:
            desc_times = sorted([int(i) for i in board_times.values()], reverse=True)
            # print(desc_times)

            sorted_slots = []

            for desc_time in desc_times:
                for slot, time in board_times.copy().items():
                    if desc_time == time and slot in board_times:
                        sorted_slots.append(slot)
                        board_times.pop(slot)

            print(sorted_slots)
            return sorted_slots
        return None

    def start(self):
        if not self.selected:
            print('Nenhuma Missão Selecionada\n')
        else:
            print('Missões Selecionadas:')
            for sq in self.selected:
                print(f'{sq[1]}: {"+" + str(sq[2]):<4} {"0/" + sq[3]:<12} {sq[4]}')
            print('')

        self.lm_pos = win32gui.GetWindowRect(self.hwnd)
        sorted_slots = self.get_sorted_time_list()
        if not sorted_slots:
            print('Nenhum tempo no quadro, dormindo por 20 minutos...\n')
            sleep(20*60)

        while sorted_slots:
            bbox = (self.lm_pos[0] + 885, self.lm_pos[1] + 354, 1, 1)
            closest_slot = sorted_slots.pop()
            self.go_to_slot(closest_slot)
            sleep(.1)
            brightness = self.check_pixel_area_brightness(bbox)

            if brightness < 127:
                active_time = self.get_active_time()
                print(f'Próxima missão em {active_time}s ({active_time // 60:02d}:{active_time % 60:02d})')
                if active_time > 5:
                    for _ in range(active_time-6):
                        sleep(1)
                    # print(active_time - 10)
                    # sleep(active_time - 5)
                    # print('Done Sleeping..')
                    self.activate_window()
                    sleep(.5)
                    self.lm_pos = win32gui.GetWindowRect(self.hwnd)
                    bbox = (self.lm_pos[0] + 885, self.lm_pos[1] + 354, 1, 1)
                    Mouse.set_pos(self.lm_pos[0] + 542, self.lm_pos[1] + 521)

                while brightness < 127:
                    # self.lm_pos = win32gui.GetWindowRect(self.hwnd)
                    brightness = self.check_pixel_area_brightness(bbox)
                details = self.get_quest_name()
                print(details + '\n')
            else:
                details = self.get_quest_name()
                print(details + '\n')

        self.start()

    @staticmethod
    def check_pixel_area_brightness(bbox):
        area = {"left": bbox[0], "top": bbox[1], "width": bbox[2], "height": bbox[3]}
        img = sct.grab(area)
        # noinspection PyTypeChecker
        pixel = list(img.pixels[0][0])
        return sum(pixel) / len(pixel)

    def get_board(self):
        self.activate_window()
        self.lm_pos = win32gui.GetWindowRect(self.hwnd)
        bbox = (self.lm_pos[0] + 885, self.lm_pos[1] + 354, 1, 1)
        mousewheelcounter = 0
        quests_timers = {}
        s = perf_counter()
        for i in range(1, 21):
            x_index = i % 3
            y_index = i // 3

            Mouse.left_click(self.lm_pos[0] + self.x_coords[x_index], self.lm_pos[1] + self.y_coords[y_index])

            sleep(.05)
            brightness = self.check_pixel_area_brightness(bbox)
            # print(brightness)

            if brightness > 127:
                quest_name = self.get_quest_name()
                print(quest_name)
            else:
                result = self.get_active_time()
                print(result)
                quests_timers.update({i: result})

            if 5 <= i < 20 and i % 3 == 2:
                Mouse.wheel(7)
                mousewheelcounter += 7
                sleep(.08)

        Mouse.wheel(-35)
        print('')
        print(s - perf_counter())
        return quests_timers


pb = PushBullet()


def main():
    GuildFest()


if __name__ == '__main__':
    main()
