# -*- coding: utf-8 -*-
import os
from time import strptime, sleep
from datetime import datetime

from mss import mss
from PIL import ImageGrab
from configs import QuestDB, Pointers
from pushbullet import PushBullet
from readprocessmemory import ProcessMemory, ProcessWindow
from Mouse import Mouse

db = QuestDB()
pointers = Pointers()
sct = mss()
window = ProcessWindow('UnityWndClass', 'Lords Mobile')

if not db.selected:
    print('Nenhuma Missão Selecionada\n')
else:
    print('Missões Selecionadas:')
    for sq in db.selected:
        print(f'{sq[1]}: {"+" + str(sq[2]):<4} {"0/" + sq[3]:<12} {sq[4]}')
    print('')

slots_details = {
    1:  {'scroll': 0,  'pixel_x': 472, 'pixel_y': 383},
    2:  {'scroll': 0,  'pixel_x': 656, 'pixel_y': 383},
    3:  {'scroll': 0,  'pixel_x': 291, 'pixel_y': 636},
    4:  {'scroll': 0,  'pixel_x': 472, 'pixel_y': 636},
    5:  {'scroll': 0,  'pixel_x': 656, 'pixel_y': 636},
    6:  {'scroll': 8,  'pixel_x': 291, 'pixel_y': 614},
    7:  {'scroll': 8,  'pixel_x': 472, 'pixel_y': 614},
    8:  {'scroll': 8,  'pixel_x': 656, 'pixel_y': 614},
    9:  {'scroll': 16, 'pixel_x': 291, 'pixel_y': 596},
    10: {'scroll': 16, 'pixel_x': 472, 'pixel_y': 596},
    11: {'scroll': 16, 'pixel_x': 656, 'pixel_y': 596},
    12: {'scroll': 24, 'pixel_x': 291, 'pixel_y': 580},
    13: {'scroll': 24, 'pixel_x': 472, 'pixel_y': 580},
    14: {'scroll': 24, 'pixel_x': 656, 'pixel_y': 580},
    15: {'scroll': 32, 'pixel_x': 291, 'pixel_y': 563},
    16: {'scroll': 32, 'pixel_x': 472, 'pixel_y': 563},
    17: {'scroll': 32, 'pixel_x': 656, 'pixel_y': 563},
    18: {'scroll': 40, 'pixel_x': 291, 'pixel_y': 547},
    19: {'scroll': 40, 'pixel_x': 472, 'pixel_y': 547},
    20: {'scroll': 40, 'pixel_x': 656, 'pixel_y': 547},
}


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


def get_pixel_brightness(x, y):
    area = {"left": x, "top": y, "width": 1, "height": 1}
    img = sct.grab(area)
    # noinspection PyTypeChecker
    pixel = list(img.pixels[0][0])
    return sum(pixel) / len(pixel)


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

    def get_clock(self):
        module, base_pointer, pointers_ = pointers.get_pointers('clock')
        dll_base_address = self.lm.get_module_address_by_name(module)
        address = self.get_pointer(dll_base_address + base_pointer, pointers_)
        value = self.lm.read_4_bytes(address)
        # time = strptime(value, '%M:%S').tm_sec + strptime(value, '%M:%S').tm_min * 60
        return value

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

    '''def get_slot_time(self, slot):
        if isinstance(slot, Slot):
            number = slot.number
        elif isinstance(slot, int):
            number = slot
        else:
            return
        pointer_name = f'slot_{number%9}'
        module, base_pointer, pointers_ = pointers.get_pointers(pointer_name)
        dll_base_address = self.lm.get_module_address_by_name(module)
        address = self.lm.get_pointer(dll_base_address + base_pointer, pointers_)
        value = self.lm.read_string(address, 5)
        time = strptime(value, '%M:%S').tm_sec + strptime(value, '%M:%S').tm_min * 60
        return time

    def get_slot_points(self, slot):
        if isinstance(slot, Slot):
            number = slot.number
        elif isinstance(slot, int):
            number = slot
        else:
            return
        pointer_name = f'slot_{number%9}'
        module, base_pointer, pointers_ = pointers.get_pointers(pointer_name)
        pointers_[2] += 8
        pointers_[6] += 2
        dll_base_address = self.lm.get_module_address_by_name(module)
        address = self.lm.get_pointer(dll_base_address + base_pointer, pointers_)
        value = self.lm.read_string(address, 5)
        return value'''


class Slot:
    def __init__(self, number, scroll, x, y):
        self.number = number
        self.scroll = scroll
        self.x = x
        self.y = y
        self.timer = -1
        self.points = 0
        self.details = {}
        self.target = -1


class GuildFest(LMReadMemory):
    def __init__(self):
        super(GuildFest, self).__init__()
        self.slots = [Slot(number, details['scroll'], details['pixel_x'], details['pixel_y'])
                      for number, details in slots_details.items()]
        # print(self.slots)
        self.current_scroll = 0
        self.current_slot = None
        self.sorted_slots = []
        self.lm_pos = window.get_position()
        self.d_time = ''

    def get_the_mission(self, slot=None, text='', quest_id=None):
        window.get_position()
        if slot is not None:
            self.go_to_slot(slot)

        print(f'Pegando a Missão: {text}')
        Mouse.left_click(self.lm_pos[0] + 867, self.lm_pos[1] + 679)

        sleep(4)
        brightness = get_pixel_brightness(window.x + 885, window.y + 354)
        if brightness < 127:
            print('Erro ao pegar missão\n')
            return

        save_to_history(self.d_time + str(quest_id) + ' 1 ' + self.get_username)

        bbox = (window.x + 764, window.y + 329, window.x + 1114, window.y + 622)

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

            bbox = (window.x + 764, window.y + 329, window.x + 1114, window.y + 622)

            img = ImageGrab.grab(bbox=bbox)
            img.save(f'{self.d_time}.jpg')

            return f'{quest} missão não identificada'

    def go_to_slot(self, slot):
        window.activate()
        window.get_position()
        if isinstance(slot, Slot):
            self.current_slot = slot
            self.scroll_to(slot.scroll)
            # sleep(1)
            Mouse.left_click(window.x + slot.x, window.y + slot.y)
            sleep(.051)
            self.scroll_to(0)

    def get_board(self):
        for slot in self.slots:
            if slot.scroll > self.current_scroll:
                self.scroll_to(slot.scroll)
            Mouse.left_click(window.x + slot.x, window.y + slot.y)
            sleep(.1)

            if self.is_quest():
                details = self.get_mission_details()
                slot.points, slot.timer = details['Points'], -1
            else:
                timer, clock = self.get_active_time(), self.get_clock()
                target_time = clock + timer
                slot.points, slot.timer = None, timer
                slot.target = target_time

        self.scroll_to(0)
        self.sorted_slots = self.sort_slots()

    def scroll_to(self, n):
        Mouse.wheel(n - self.current_scroll, window.x + 303, window.y + 587, .008)
        self.current_scroll = n if n > 0 else 0

    def sort_slots(self):
        slots = self.slots.copy()
        slots.sort(key=lambda s: s.timer)
        self.sorted_slots = [slot for slot in slots if slot.timer >= 0][::-1]
        return self.sorted_slots

    def await_quest(self):
        Mouse.set_pos(window.x + 542, window.y + 521)

        '''if self.sorted_slots:
            slot = self.sorted_slots[::-1][0]
            self.scroll_to(slot.scroll)
            time = self.get_slot_time(slot)
            if time > 15:
                self.scroll_to(0)'''

        brightness = get_pixel_brightness(window.x + 885, window.y + 354)
        while brightness < 127:
            brightness = get_pixel_brightness(window.x + 885, window.y + 354)
        details = self.get_quest_name()
        return details

    @staticmethod
    def is_quest():
        brightness = get_pixel_brightness(window.x + 885, window.y + 354)
        if brightness < 127:
            return False
        return True


pb = PushBullet()
gf = GuildFest()
wait_th = 5*60


def main():
    window.activate()
    gf.get_board()

    if not gf.sorted_slots:
        print('Nenhum tempo no quadro, dormindo por 20 minutos...\n')
        sleep(20 * 60)

    while gf.sorted_slots:
        closest_slot = gf.sorted_slots.pop()
        gf.go_to_slot(closest_slot)

        # brightness = get_pixel_brightness(window.x + 885, window.y + 354)
        # if brightness < 127:
        if not gf.is_quest():
            active_time = gf.get_active_time()
            if active_time > wait_th:
                sleep(active_time - wait_th)
                break
            print(f'Próxima missão em {active_time}s ({active_time // 60:02d}:{active_time % 60:02d})')
            # if active_time > 5:
            #     sleep(active_time - 6)
            clock = gf.get_clock()
            while clock < closest_slot.target - 5:
                sleep(.1)
                clock = gf.get_clock()

            window.activate()
            sleep(.5)
            window.get_position()
            print(gf.await_quest())
        else:
            print(gf.get_quest_name())
    main()


if __name__ == '__main__':
    main()
