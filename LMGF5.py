import time
from Mouse import Mouse
from Process import ProcessMemory, ProcessWindow
from configs import Pointers, QuestDB


class Slot:
    def __init__(self, number, scroll, x, y):
        self.number = number
        self.scroll = scroll
        self.x = x
        self.y = y

        self.timer = None
        self.qid = None


class MemoryReader(ProcessMemory):
    def __init__(self):
        super(MemoryReader, self).__init__('Lords Mobile.exe')
        self.pointers = Pointers()

    def get_active_timer(self):
        pass


def main():
    pass



if __name__ == '__main__':
    main()
