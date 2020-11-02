import time
from Mouse import Mouse
from Process import ProcessMemory, ProcessWindow
from configs import Pointers, QuestDB
from mss import mss
from PIL import ImageGrab
import os

sct = mss()


def get_pixel_brightness(x, y):
    area = {"left": x, "top": y, "width": 1, "height": 1}
    img = sct.grab(area)
    # noinspection PyTypeChecker
    pixel = list(img.pixels[0][0])
    return sum(pixel) / len(pixel)


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
        self.qid = None

    def __repr__(self):
        return f'Slot: {self.number:>2} | x: {self.x:>3} | y: {self.y:>3} | scroll: {self.scroll:>2}'


class MemoryReader(ProcessMemory):
    def __init__(self):
        super(MemoryReader, self).__init__('Lords Mobile.exe')
        self.pointers = Pointers()

    def get_clock(self):
        # get pointer
        module, base_pointer, pointers_ = self.pointers.get_pointer_by_name('clock')

        # read value at address
        module_addr = self.get_module_address_by_name(module)
        address = self.get_pointer(module_addr + base_pointer, pointers_)
        value = self.read_4_bytes(address)

        return value

    def get_active_timer(self):
        # get pointer
        module, base_pointer, pointers_ = self.pointers.get_pointer_by_name('active_time')

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
            module, base_pointer, pointers_ = self.pointers.get_pointer_by_name(name)

            # read string at address
            module_addr = self.get_module_address_by_name(module)
            addr = self.get_pointer(module_addr + base_pointer, pointers_)
            value = self.read_string(addr+offset*2, size-offset)
            result.append(value)

        return result

    def get_player_name(self):
        # get pointer
        module, base_pointer, pointers_ = self.pointers.get_pointer_by_name('player_name')

        # get value at address
        module_addr = self.get_module_address_by_name(module)
        addr = self.get_pointer(module_addr + base_pointer, pointers_)
        value = self.read_string(addr, 12)

        return value


class GuildFest:
    def __init__(self):
        self.running = True

        self.slots = [Slot(number) for number in Slot.details.keys()]
        self.sorted_slots = None
        self.current_slot = None

        self.window = ProcessWindow('UnityWndClass', 'Lords Mobile')
        self.memory = MemoryReader()
        self.db = QuestDB()

        self.current_scroll = 0

    def get_board(self):
        for slot in self.slots:
            self.scroll(slot.scroll)
            Mouse.left_click(self.window.x + slot.x, self.window.y + slot.y)
            self.current_slot = slot

            time.sleep(.1)
            if self.is_quest():
                self.identify_quest()
                # slot.timer = None
                # slot.target = None
                # slot.qid = self.identify_quest()
                #
                # self.get_quest_name(slot.qid)
                # if self.is_selected(slot.qid):
                #     self.get_the_quest()

            else:
                timer, clock = self.memory.get_active_timer(), self.memory.get_clock()
                slot.timer = timer
                slot.target = clock + timer
                slot.qid = None

        self.sort_slots()
        self.scroll(0)

    def identify_quest(self):
        slot = self.current_slot
        details = self.memory.get_mission_details()
        qid = self.db.identify_quest(*details)

        slot.timer = None
        slot.target = None
        slot.qid = qid

        self.get_quest_name(slot.qid)
        if self.is_selected(slot.qid):
            self.get_the_quest()

        self.get_quest_name(qid)

        return qid

    def get_quest_name(self, qid):
        print(self.db.get_quest_by_id(qid))

    def is_selected(self, qid):
        return qid in self.db.get_selected_ids()

    def get_the_quest(self):
        Mouse.left_click(self.window.x + 867, self.window.y + 679)

        time.sleep(4)
        brightness = get_pixel_brightness(self.window.x + 885, self.window.y + 354)
        if brightness < 127:
            print('Erro ao pegar missão\n')
            return

        img = ImageGrab.grab(self.window.x + 764, self.window.y + 329, self.window.x + 1114, self.window.y + 622)
        img.save('temp.jpeg')

        # pb.push_img('tempimage.jpeg', title=f'Missão Pronta [{self.get_username}]', body=text)
        # pb.push_img('tempimage.jpeg', email='thallesrafael1402@gmail.com',
        #            title=f'Missão Pronta [{self.get_username}]', body=text)

        # os.remove('temp.jpeg')

        print(self.db.get_quest_by_id(self.current_slot.qid))

        self.running = False

    def sort_slots(self):
        self.sorted_slots = [slot for slot in self.slots.copy() if slot.timer is not None]
        self.sorted_slots.sort(key=lambda s: s.timer, reverse=True)

    def go_to_slot(self, slot: Slot):
        self.window.activate()
        self.window.get_position()

        self.current_slot = slot

        self.scroll(slot.scroll)

        Mouse.left_click(self.window.x + slot.x, self.window.y + slot.y)
        time.sleep(.051)

        self.scroll(0)

    def wait_quest(self):
        Mouse.set_pos(self.window.x + 542, self.window.y + 521)

        brightness = get_pixel_brightness(self.window.x + 885, self.window.y + 354)

        timer = time.perf_counter()
        while brightness < 127:
            brightness = get_pixel_brightness(self.window.x + 885, self.window.y + 354)
            if time.perf_counter()-timer > 10:
                break
        else:
            if self.is_selected(self.identify_quest()):
                self.get_the_quest()

    def scroll(self, clicks):
        Mouse.wheel(clicks - self.current_scroll, self.window.x + 303, self.window.y + 587, .008)
        self.current_scroll = clicks if clicks > 0 else 0

    def is_quest(self):
        brightness = get_pixel_brightness(self.window.x + 885, self.window.y + 354)
        if brightness < 127:
            return False
        return True


def main():
    wait_timer = 2*60
    fg = GuildFest()
    check_slot = 0

    while fg.running:
        fg.window.activate()
        fg.get_board()

        while fg.sorted_slots:
            # print(check_lowest)
            slot = fg.sorted_slots.pop()
            fg.go_to_slot(slot)

            if fg.is_quest():
                if fg.is_selected(fg.identify_quest()):
                    fg.get_the_quest()
            else:
                active_timer = fg.memory.get_active_timer()
                print(check_slot)
                if active_timer > wait_timer and check_slot != slot.number:
                    check_slot = slot.number
                    break
                elif active_timer > wait_timer and check_slot == slot.number:
                    time.sleep(active_timer - wait_timer)

                clock = fg.memory.get_clock()
                while clock < slot.target - 5:
                    clock = fg.memory.get_clock()

                fg.window.activate()
                time.sleep(.5)
                fg.window.get_position()
                fg.wait_quest()





if __name__ == '__main__':
    main()
