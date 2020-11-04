import sqlite3
import tkinter as tk
import random
import datetime
from databases import QuestDB
from PIL import ImageTk, Image
db = QuestDB()

if __name__ == '__main__':
    top = tk.Tk
else:
    top = tk.Toplevel

def generate_test():
    names = ['Khemmis', 'THALLES 14', 'Dodie', 'xleo2']
    time_now = int(datetime.datetime.now().timestamp())
    slots = {1:'q',2:'q',3:'q',4:'q',5:'q',6:'q',7:'q',8:'q',9:'q',10:'q',11:'q',12:'q',13:'q',14:'q',15:'q',16:'q',17:'q',18:'q',19:'q',20:'q',21:'q'}

    with open('test.txt', 'a') as f:
        f.write(f'{random.choice(names)}|{time_now}|{",".join([str(random.randint(1, 290)) for _ in range(5)])}:')

    values = []
    for i in range(300):
        slot, identify = random.choice(list(slots.items()))
        if identify == 'q':
            time = 30*60
            slots.update({slot: 't'})
            value = random.randint(1, 290)
        else:
            time = random.randint(1, 30*60)
            slots.update({slot: 'q'})
            value = 30*60
        values.append(f'{time}.{slot}.{identify}.{value}')

    with open('test.txt', 'a') as f:
        f.write('|'.join(values)+'\n')


#generate_test()


class Label(tk.Label):
    def __init__(self, parent, **kw):
        super(Label, self).__init__(parent)
        self.configure(
            bg='light pink',
            font=('Gadugi', 12, 'bold')
        )
        self.config(**kw)


class Slot(tk.Label):
    def __init__(self, parent, number, **kw):
        super(Slot, self).__init__(parent)
        self.config(**kw)
        self.number = number
        self.qid = None
        self.timer = None
        self.sequence = []


class GUI(top):
    def __init__(self, parent=None):
        super(GUI, self).__init__(parent)
        g = ChooseGUI(self)

        self.minsize(500, 500)
        self.images = set([])

        self.slots = {}
        self.name = ''
        self.sequence = []
        self.counter = 1

        self.board_frame = tk.Frame(self, bg='yellow')
        self.board_frame.place(relx=0, rely=0, relwidth=.66, relheight=1)

        self.quest_frame = tk.Frame(self, bg='light cyan')
        self.quest_frame.place(relx=.66, rely=0, relwidth=.34, relheight=.5)

        self.controls_frame = tk.Frame(self, bg='lemon chiffon')
        self.controls_frame.place(relx=.66, rely=.5, relwidth=.34, relheight=.5)

        self.populate_board_frame()
        # self.parse()
        # self.update()

    def populate_board_frame(self):
        for i in range(22):
            slot = Slot(self.board_frame, i, bg='cyan', compound='top')
            slot.place(relx=i % 3 / 3, rely=i // 3 / 7, relwidth=1/3-.01, relheight=1/7-.01)
            self.slots.update({i: slot})
    #
    # def parse(self):
    #     with open('test.txt', 'r') as f:
    #         line = f.readline()
    #
    #     sep = line.find(':')
    #     self.name = line[:sep]
    #     self.sequence = (i for i in line[sep+1:].split('|'))
    #     print(self.sequence)
    #
    # def update(self):
    #     print(self.counter)
    #     self.counter += 1
    #
    #     item = next(self.sequence).strip()
    #     if not item:
    #         return
    #
    #     clock, slot, value = item.split('.')
    #     if value.startswith('q'):
    #         qid = value[1:]
    #         _, text, points, *_, img_index, _ = db.get_quest_by_id(qid)
    #
    #         bg = 'goldenrod'
    #         text = f'+{points}'
    #         self.update_current_quest(qid=qid)
    #     else:
    #         value = int(value[1:])
    #         text = f'{value // 60:02d}:{value % 60:02d}'
    #         bg = 'orange4'
    #         self.update_current_quest(timer=value)
    #
    #     slot = self.slots.get(int(slot))
    #     slot.configure(text=text, bg=bg, fg='white', compound='top', font=('Gadugi', 16, 'bold'))
    #
    #     self.after(100, self.update)
    #
    # def update_current_quest(self, qid=None, timer=None):
    #     if qid is not None:
    #         _, name, points, req, time, *_, quest_img, icon_img = db.get_quest_by_id(qid)
    #         print(name, points, req, time, quest_img, icon_img)
    #         [w.destroy() for w in self.quest_frame.pack_slaves()]
    #
    #         quest_img = ImageTk.PhotoImage(Image.open(f'imgs\\quests\\{quest_img:03d}.png'))
    #         points_img = ImageTk.PhotoImage(Image.open(f'imgs\\icons\\066.png').resize((20, 20)))
    #         req_img = ImageTk.PhotoImage(Image.open(f'imgs\\icons\\{35:03d}.png').resize((20, 20)))
    #         time_img = ImageTk.PhotoImage(Image.open(f'imgs\\icons\\011.png').resize((20, 20)))
    #
    #         name_label = Label(self.quest_frame, text=name, compound='top', image=quest_img)
    #         name_label.pack(fill='both', expand=1)
    #         name_label.image = quest_img
    #
    #         points_label = Label(self.quest_frame, text=f'+{points}', compound='left', image=points_img)
    #         points_label.pack(fill='both', expand=1)
    #         points_label.image = points_img
    #
    #         req_label = Label(self.quest_frame, text=f'0 / {req}', compound='left', image=req_img)
    #         req_label.pack(fill='both', expand=1)
    #         req_label.image = req_img
    #
    #         time_label = Label(self.quest_frame, text=time, compound='left', image=time_img)
    #         time_label.pack(fill='both', expand=1)
    #         time_label.image = time_img
    #
    #     elif timer is not None:
    #         [w.destroy() for w in self.quest_frame.pack_slaves()]
    #         timer_label = Label(self.quest_frame, text=timer, bg='light cyan')
    #         timer_label.pack(fill='both', expand=1)
    #     else:
    #         pass


class ChooseGUI(tk.Toplevel):
    def __init__(self, parent):
        self.parent = parent
        super(ChooseGUI, self).__init__(parent)

        self.listbox = tk.Listbox(self)
        self.listbox.pack()

        self.populate_listbox()

    def populate_listbox(self):
        with open('test.txt', 'r') as f:
            while True:
                print(f.readline(100))


if __name__ == "__main__":
    GUI().mainloop()
