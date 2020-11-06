import sqlite3
import tkinter as tk
from tkinter import ttk
import random
import datetime
from databases import QuestDB, HistoryDB
from PIL import ImageTk
from functions import load_icon_image, load_quest_image


db = QuestDB()
hist = HistoryDB()

if __name__ == '__main__':
    top = tk.Tk
else:
    top = tk.Toplevel


def generate_history():
    names = ['Khemmis', 'THALLES 14', 'Dodie', 'xleo2']
    time_now = int(datetime.datetime.now().timestamp())
    slots = {1:'q',2:'q',3:'q',4:'q',5:'q',6:'q',7:'q',8:'q',9:'q',10:'q',11:'q',12:'q',13:'q',14:'q',15:'q',16:'q',17:'q',18:'q',19:'q',20:'q',21:'q'}

    sid = hist.get_highest_sid() + 1
    print(sid)
    name = random.choice(names)

    hist.insert_session(sid, name, time_now, [str(random.randint(1, 290)) for _ in range(random.randint(0, 5))])

    for i in range(random.randint(10, 300)):
        slot, identifier = random.choice(list(slots.items()))

        time = random.randint(1, 60*60)
        value = 30*60 if identifier == 't' else random.randint(1, 290)
        if identifier == 't':
            slots.update({slot: 'q'})
        else:
            slots.update({slot: 't'})

        hist.insert_history(sid, time, identifier, slot, value)


class Label(tk.Label):
    def __init__(self, parent, **kw):
        super(Label, self).__init__(parent)
        self.configure(
            bg='light pink',
            font=('Gadugi', 12, 'bold')
        )
        self.config(**kw)
        self.qid = None


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

        self.minsize(500, 500)

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


class ScrollFrame(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, **kw)
        self.y_list = [0, 0]
        self.scroll_units = 1
        self.config(relief='flat', borderwidth=0)
        self.canvas = tk.Canvas(self, borderwidth=0, relief='flat', highlightthickness=0)
        self.viewPort = tk.Frame(self.canvas, relief='flat', borderwidth=0)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.scrollbar_scroll, width=20)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=1)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.viewPort, anchor="nw", tags="self.viewPort")

        self.viewPort.bind("<Configure>", lambda e: self.on_frame_configure())
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        self.on_frame_configure()

    def bind_scroll(self, obj):
        obj.bind('<B1-Motion>', self.drag_and_scroll)
        obj.bind('<MouseWheel>', self.on_scroll)

    def on_frame_configure(self):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def drag_and_scroll(self, event):
        y = event.y
        widget = str(event.widget)
        if '!canvas' in widget and 'combobox' not in widget:
            self.y_list[1] += y
            self.scroll()

    def scroll(self):
        *_, start, end = self.canvas.bbox('all')
        vsb_start, vsb_end = self.vsb.get()

        number = (self.y_list[1] - self.y_list[0])

        if 1 < abs(number) < 750 and end > 500:
            new_start = number*-1*1.1/end + vsb_start

            self.canvas.yview_moveto(new_start)

        self.y_list[0] = self.y_list[1]

    def on_scroll(self, event):
        widget = str(event.widget)
        if '!canvas' in widget and 'combobox' not in widget:
            delta = event.delta
            unit = -self.scroll_units if delta > 0 else self.scroll_units
            self.canvas.yview_scroll(unit, 'units')

    def scrollbar_scroll(self, *args):
        if args[0] == 'scroll':
            unit = -self.scroll_units if int(args[1]) < 0 else self.scroll_units
            self.canvas.yview_scroll(unit, 'units')
        else:
            self.canvas.yview(*args)


class ChooseGUI(top):
    def __init__(self, parent=None):
        self.parent = parent
        super(ChooseGUI, self).__init__(parent)
        self.geometry('850x500+600+100')

        self.treeview = None

        self.create_treeview()
        self.summaries = SessionSummary(self, bg='red')
        self.summaries.place(x=350, rely=0, width=500, relheight=1)

        self.populate_treeview()
        self.listener()

    def create_treeview(self):
        self.treeview = treeview = ttk.Treeview(self, columns=('name', 'date', 'time'))
        treeview.place(relx=0, rely=0, width=350, relheight=1)

        treeview.heading('#0', anchor='center', text='')
        treeview.heading('name', anchor='center', text='Nome')
        treeview.heading('date', anchor='center', text='Data')
        treeview.heading('time', anchor='center', text='Hora')

        treeview.column('#0', minwidth=0, width=0, stretch=0, anchor='center')
        treeview.column('name', minwidth=100, width=100, stretch=0, anchor='center')
        treeview.column('date', minwidth=100, width=150, stretch=0, anchor='center')
        treeview.column('time', minwidth=100, width=100, stretch=0, anchor='center')

    def populate_treeview(self):
        for session in hist.get_sessions()[::-1]:
            sid, name, timestamp, *_ = session

            timestamp = datetime.datetime.fromtimestamp(timestamp)
            self.treeview.insert('', 'end', sid, values=(name, f'{timestamp:%d de %B, %Y}', f'{timestamp:%H:%M:%S}'))

    def listener(self):
        # print(self.summaries.sid)
        sid = self.treeview.selection()
        if sid:
            sid = sid[0]
            if self.summaries.sid != sid:
                self.summaries.sid = sid
        self.after(50, self.listener)


class SessionSummary(tk.Frame):
    def __init__(self, parent, **kw):
        super(SessionSummary, self).__init__(parent, **kw)

        self._selected = None
        self._sid = None
        self.scrollframe = None
        self.selected_imgs = []
        self.sel_label_var = tk.StringVar(self)
        self.sel_name_var = tk.StringVar(self)
        self.sel_req_var = tk.StringVar(self)

        self.selected_frame = tk.Frame(self, bg='pink')
        self.selected_frame.place(relx=0, rely=0, width=500, height=200)

        self.summary_frame = tk.Frame(self, bg='cyan')
        self.summary_frame.place(relx=0, y=200, width=500, height=300)

        self.populate_selected_frame()
        self.populate_summary_frame()

    def populate_selected_frame(self):
        label = Label(self.selected_frame, textvariable=self.sel_label_var)
        label.pack(fill='x')

        frame = tk.Frame(self.selected_frame, bg='black')
        frame.pack(fill='both', expand=1)

        self.scrollframe = ScrollFrame(frame)
        self.scrollframe.place(relx=0, rely=0, relwidth=.65, relheight=1)

        details_frame = tk.Frame(frame, bg='light cyan')
        details_frame.place(relx=.65, rely=0, relwidth=.35, relheight=1)
        self.update_idletasks()

        name_label = Label(details_frame, textvariable=self.sel_name_var, wraplength=150)
        name_label.pack(fill='both', expand=1)

        req_label = Label(details_frame, textvariable=self.sel_req_var, compound='left', wraplength=150)
        req_label.pack(fill='both', expand=1)

    def populate_summary_frame(self):
        pass

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, values: iter):
        self._selected = values
        # destroy previous widgets
        [widget.destroy() for widget in self.scrollframe.viewPort.grid_slaves()]

        cols = 4
        width = self.scrollframe.viewPort.winfo_width()/cols
        for n, qid in enumerate(values):
            self.scrollframe.viewPort.grid_columnconfigure(n % cols, minsize=width)

            _, _, points, *_, quest_icon, _ = db.get_quest_by_id(qid)

            img = ImageTk.PhotoImage(load_quest_image(quest_icon, width=width-10))
            label = Label(self.scrollframe.viewPort, compound='top', text=f'+{points}', image=img)
            label.grid(row=n // cols, column=n % cols, sticky='nswe')

            label.bind('<Enter>', lambda e, num=qid: self.update_sel_labels(e, num))
            label.image = img

        self.sel_label_var.set(f'{len(values)} missões selecionadas')

    def update_sel_labels(self, event, qid):
        _, name, _, req, *_ = db.get_quest_by_id(qid)
        self.sel_name_var.set(name)
        self.sel_req_var.set(f'0 / {req}')

    @property
    def sid(self):
        return self._sid

    @sid.setter
    def sid(self, value):
        self._sid = value
        session = hist.get_session_by_sid(value)
        history = hist.get_history_by_sid(value)

        self.selected = [int(i) for i in str(session[-2]).split(',') if i]
        sum = 0
        quests = 0
        for i in history:
            sum += i[1]
            quests += 1 if i[2] == 'q' else 0

        print(sum/60/60, quests)

        # print(session)
        # print(len(history))


if __name__ == "__main__":
    ChooseGUI().mainloop()
