import time
from lib.Mouse import Mouse
from lib.Process import ProcessMemory, ProcessWindow
from lib.databases import QuestDB, HistoryDB, LocalDB
from mss import mss
from PIL import ImageGrab
import os
from lib import pushbullet
import sys
from lib.functions import game_registry_search
from lib.configs import load_game_languages, load_configs, Pointers


def get_game_language():
    return game_registry_search('Other_Language')['Other_Language']


def get_game_res():
    result = game_registry_search('Width', 'Height')

    return result['Width'], result['Height']


def get_pixel_brightness(x, y):
    area = {"left": x, "top": y, "width": 1, "height": 1}
    img = sct.grab(area)
    # noinspection PyTypeChecker
    pixel = list(img.pixels[0][0])
    return sum(pixel) / len(pixel)


def handle_close(text=None):
    sys.exit(text)


if load_configs()['pointers_from_github']:
    Pointers.get_pointers()


pb = pushbullet.PushBullet()
sct = mss()
hist = HistoryDB()
db = QuestDB()
local = LocalDB().get_main_localization()
start = 0


def validate_start():
    all_langs = load_game_languages()
    current_lang = all_langs[get_game_language()]
    available_langs = db.get_ambig_langs()

    if current_lang[0] not in available_langs:
        text = f'({current_lang[1]}) {local["lang_not_supported"]}\n'\
               f'{local["supported_langs"]}: '\
               f'{", ".join([lang[1] for lang in all_langs.values() if lang[0] in available_langs])}'
        handle_close(text)
    db.game_lang = current_lang[0]

    width, height = get_game_res()
    if width != 1280 or height != 720:
        text = f'{local["wrong_res"]}: {width}x{height}\n{local["use"]} 1280x720'
        handle_close(text)


class Slot:
    details = {
        1: {'scroll': 0, 'pixel_x': 472, 'pixel_y': 383},
        2: {'scroll': 0, 'pixel_x': 656, 'pixel_y': 383},
        3: {'scroll': 0, 'pixel_x': 291, 'pixel_y': 636},
        4: {'scroll': 0, 'pixel_x': 472, 'pixel_y': 636},
        5: {'scroll': 0, 'pixel_x': 656, 'pixel_y': 636},
        6: {'scroll': 8, 'pixel_x': 291, 'pixel_y': 614},
        7: {'scroll': 8, 'pixel_x': 472, 'pixel_y': 614},
        8: {'scroll': 8, 'pixel_x': 656, 'pixel_y': 614},
        9: {'scroll': 16, 'pixel_x': 291, 'pixel_y': 596},
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

    def __init__(self, number):
        self.number = number
        d = Slot.details.get(number)

        self.scroll = d.get('scroll')
        self.x = d.get('pixel_x')
        self.y = d.get('pixel_y')

        self.timer = None
        self.target = None
        self.qid = None

    def __repr__(self):
        return f'Slot: {self.number:>2} | x: {self.x:>3} | y: {self.y:>3} | scroll: {self.scroll:>2}'


class MemoryReader(ProcessMemory):
    def __init__(self):
        super(MemoryReader, self).__init__('Lords Mobile.exe')

    def get_clock(self):
        # get pointer
        module, base_pointer, pointers_ = Pointers.get_pointer_by_name('clock')

        # read value at address
        module_addr = self.get_module_address_by_name(module)
        address = self.get_pointer(module_addr + base_pointer, pointers_)
        value = self.read_4_bytes(address)

        return value

    def get_active_timer(self):
        # get pointer
        module, base_pointer, pointers_ = Pointers.get_pointer_by_name('active_time')

        # read value at address
        module_addr = self.get_module_address_by_name(module)
        address = self.get_pointer(module_addr + base_pointer, pointers_)
        value = self.read_string(address, 5)

        # convert value to int (seconds)
        minutes, seconds = value.split(':')
        timer = int(minutes)*60 + int(seconds)

        return timer

    def get_mission_details(self):
        """{pointer_name: (string_length, offset)}"""
        pointers = {'quest_points': (4, 1), 'quest_requirements': (20, 4), 'quest_time': (11, 0)}

        result = []
        for name, values in pointers.items():
            size, offset = values

            # get pointer
            module, base_pointer, pointers_ = Pointers.get_pointer_by_name(name)

            # read string at address
            module_addr = self.get_module_address_by_name(module)
            addr = self.get_pointer(module_addr + base_pointer, pointers_)
            value = self.read_string(addr+offset*2, size-offset)
            result.append(value)

        return result

    def get_player_name(self):
        # get pointer
        module, base_pointer, pointers_ = Pointers.get_pointer_by_name('player_name')

        # get value at address
        module_addr = self.get_module_address_by_name(module)
        addr = self.get_pointer(module_addr + base_pointer, pointers_)
        value = self.read_string(addr, 12)

        return value

    def get_quest_name(self):
        # get pointer
        module, base_pointer, pointers_ = Pointers.get_pointer_by_name('quest_name')

        # get value at address
        module_addr = self.get_module_address_by_name(module)
        addr = self.get_pointer(module_addr + base_pointer, pointers_)
        value = self.read_string(addr, 200)

        return value


class GuildFest:
    def __init__(self):
        self.running = True

        self.slots = [Slot(number) for number in Slot.details.keys()]
        self.sorted_slots = None
        self.current_slot = None

        self.window = ProcessWindow('UnityWndClass', 'Lords Mobile')
        self.memory = MemoryReader()

        self.current_scroll = 0

    def get_board(self):
        # gets timers and quests from the entire board
        for slot in self.slots:
            self.scroll(slot.scroll)
            Mouse.left_click(self.window.x + slot.x, self.window.y + slot.y)
            self.current_slot = slot

            time.sleep(.1)
            if self.is_quest():
                self.identify_quest()
            else:
                self.get_timer()

        self.sort_slots()
        self.scroll(0)

    def identify_quest(self):
        # identifies quest and configures slot
        slot = self.current_slot
        details = self.memory.get_mission_details()
        name = self.memory.get_quest_name()
        qid = db.identify_quest(*details, name)

        slot.timer = None
        slot.target = None
        slot.qid = qid

        save_name(qid, name, db.game_lang)
        save_history(hist.get_highest_sid(), self.current_slot, time.time() - start)

        print(self.get_quest_name(slot.qid), name)
        if self.is_selected(slot.qid):
            self.get_the_quest()

        return qid

    def get_timer(self):
        # gets timer and configures slot
        timer, clock = self.memory.get_active_timer(), self.memory.get_clock()
        self.current_slot.timer = timer
        self.current_slot.target = clock + timer
        self.current_slot.qid = None

        save_history(hist.get_highest_sid(), self.current_slot, time.time() - start)

    @staticmethod
    def get_quest_name(qid):
        _, name, points, *_ = db.get_quest_by_id(qid)
        return f'{name}, +{points}'

    @staticmethod
    def is_selected(qid):
        return qid in db.get_selected_ids()

    def get_the_quest(self):
        # gets the quest and exits the program
        Mouse.left_click(self.window.x + 867, self.window.y + 679)

        time.sleep(4)
        brightness = get_pixel_brightness(self.window.x + 885, self.window.y + 354)
        if brightness < 127:
            print('Erro ao pegar missão\n')
            return

        self.screenshot_quest()
        self.pushbullet()
        os.remove('temp.jpeg')

        handle_close()

    def pushbullet(self):
        # notifies the user on pushbullet
        text = f'{self.get_quest_name(self.current_slot.qid)} {self.memory.get_player_name()}'
        pb.push_img('temp.jpeg', title=text)
        pb.push_img('temp.jpeg', email='thallesrafael1402@gmail.com', title=text)

    def sort_slots(self):
        # sort slots based on time to appear
        self.sorted_slots = [slot for slot in self.slots.copy() if slot.timer is not None]
        self.sorted_slots.sort(key=lambda s: s.timer, reverse=True)

    def go_to_slot(self, slot: Slot):
        # scrolls down to a slot, clicks it and goes back to the top of the page
        self.window.activate()
        self.window.get_position()

        self.current_slot = slot

        self.scroll(slot.scroll)

        Mouse.left_click(self.window.x + slot.x, self.window.y + slot.y)
        time.sleep(.051)

        self.scroll(0)

    def wait_quest(self):
        Mouse.set_pos(self.window.x + 542, self.window.y + 521)

        # waits for quest to appear. If it takes more than 10 seconds, move on because it most likely didn't appear
        brightness = get_pixel_brightness(self.window.x + 885, self.window.y + 354)
        timer = time.perf_counter()
        while brightness < 127:
            brightness = get_pixel_brightness(self.window.x + 885, self.window.y + 354)
            if time.perf_counter()-timer > 10:
                break
        else:
            self.identify_quest()

    def scroll(self, clicks):
        # scroll to a slot base on its clicks
        Mouse.wheel(clicks - self.current_scroll, self.window.x + 303, self.window.y + 587, .008)
        self.current_scroll = clicks if clicks > 0 else 0

    def is_quest(self):
        # checks if the current selected slot contais a quest
        brightness = get_pixel_brightness(self.window.x + 885, self.window.y + 354)
        if brightness < 127:
            return False
        return True

    def screenshot_quest(self):
        # take a screenshot of the quest
        img = ImageGrab.grab(bbox=(self.window.x + 764, self.window.y + 329, self.window.x + 1114, self.window.y + 622))
        img.save('temp.jpeg')


def save_history(sid, slot: Slot, _time):
    _time = int(_time)
    last_identifier = hist.get_last_identifier(sid, slot.number)
    if slot.timer is not None:
        # if last_identifier == 't':
        #     return

        hist.insert_history(sid, _time, 't', slot.number, slot.timer)

    elif slot.qid is not None:
        if last_identifier == 'q':
            return

        hist.insert_history(sid, _time, 'q', slot.number, slot.qid)


def main():
    validate_start()

    wait_timer = 5*60
    fg = GuildFest()
    check_slot = 0

    # create "session" for history
    global start
    start = int(time.time())
    selected = db.get_selected_ids()
    sid = hist.get_highest_sid() + 1
    hist.insert_session(sid, fg.memory.get_player_name(), start, selected)

    while True:
        fg.window.activate()
        fg.get_board()
        # for slot in fg.slots:
        #     save_history(sid, slot, time.time() - start)

        while fg.sorted_slots:
            slot = fg.sorted_slots.pop()
            fg.go_to_slot(slot)

            if fg.is_quest():
                if fg.is_selected(fg.identify_quest()):
                    fg.get_the_quest()
            else:
                # if time > wait_timer get the board again to make sure the it was in the right slot
                active_timer = fg.memory.get_active_timer()
                if active_timer > wait_timer and check_slot != slot.number:
                    check_slot = slot.number
                    break
                elif active_timer > wait_timer and check_slot == slot.number:
                    time.sleep(active_timer - wait_timer)

                # if time < wait_timer wait until game clock == slot target
                clock = fg.memory.get_clock()
                while clock < slot.target - 5:
                    clock = fg.memory.get_clock()

                # activate window and wait for quest to appear
                fg.window.activate()
                time.sleep(.5)
                fg.window.get_position()
                fg.wait_quest()


if __name__ == '__main__':
    main()
