import sqlite3
import tkinter as tk
from tkinter import ttk
import random
import datetime
from databases import QuestDB, HistoryDB, LocalDB
from PIL import ImageTk
from functions import load_icon_image, load_quest_image
import cwidgets as cw
import time


db = QuestDB()
hist = HistoryDB()
local = LocalDB().get_main_localization()

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


class Label(cw.Label):
    def __init__(self, parent, **kw):
        super(Label, self).__init__(parent)
        self.config(**kw)
        self.qid = None


class Slot(cw.Label):
    def __init__(self, parent, number, **kw):
        super(Slot, self).__init__(parent)
        self.config(**kw)
        self.number = number
        self._qid = None
        self._timer = None
        self.sequence = []
        self.current = -1
        self.speed = 100
        self.quest_timer = 0
        self.after_schedule = None
        self.image = None

    def __str__(self):
        return f'{self._qid}: {self.sequence[self.current]}'

    def insert(self, deltatime, identifier, value):
        if not self.sequence:
            self.sequence.append((0, identifier, value))
            if identifier == 'q':
                return deltatime, value
        else:
            last = self.sequence[-1]
            last_deltatime, last_id, last_value = last

            if last_id == identifier and value <= last_value:
                # Invalid record
                pass
            else:
                if identifier == 'q':
                    new = (last_deltatime + last_value, 'q', value)
                else:
                    difference = 1800 - value
                    new = (deltatime - difference, 't', 1800)

                self.sequence.append(new)
                if identifier == 'q':
                    return deltatime, value
                # print(current)

    def update(self):
        deltatime, identifier, value = self.sequence[self.current]

        if identifier == 'q':
            bg = cw.DARK_BLUE

            *_, img_index, _ = db.get_quest_by_id(value)
            image = load_quest_image(img_index, 60)
            self.image = ImageTk.PhotoImage(image)

            self.config(bg=bg, image=self.image)

            self.qid = value
        else:
            bg = cw.DARK_BLUE
            image = load_icon_image(67, 40)
            self.image = ImageTk.PhotoImage(image)

            self.configure(bg=bg, image=self.image)

            self.timer = value

    def next(self):
        if self.current < len(self.sequence) -1:
            self.current += 1
            self.update()

    def get_next(self):
        if self.current < len(self.sequence) -1:
            return self.sequence[self.current+1]

    def previous(self):
        if self.current > 0:
            self.current -= 1
            self.update()

    def get_previous(self):
        if self.current > 0:
            return self.sequence[self.current]

    def autoplay(self):
        if self.timer is not None:
            self.timer -= 1
            if self.timer == 0:
                self.next()

        if self.qid is not None:
            self.quest_timer -= 1
            if self.quest_timer == 0:
                self.next()

        self.after_schedule = self.after(int(1000/self.speed), self.autoplay)
        if len(self.sequence) - 1 == self.current:
            self.after_cancel(self.after_schedule)

    @property
    def timer(self):
        return self._timer

    @timer.setter
    def timer(self, value: int):
        self._qid = None
        self._timer = value
        minute, second = value // 60, value % 60

        value = f'{minute:02d}:{second:02d}'
        self.config(text=value)

    @property
    def qid(self):
        return self._qid

    @qid.setter
    def qid(self, value: int):
        self._timer = None
        self._qid = value

        value = f'+{db.get_quest_points(value)}'

        self.config(text=value)

        start = self.sequence[self.current][0]
        if self.current + 1 >= len(self.sequence):
            return

        finish = self.sequence[self.current + 1][0]
        self.quest_timer = finish - start


class History(tk.Toplevel):
    def __init__(self, sid, parent=None):
        self.parent = parent
        super(History, self).__init__(parent)

        # self.minsize(650, 500)
        self.geometry('900x500')
        self.resizable(0, 0)

        self.sid = sid
        self.slots = {}
        self.name = ''
        self.counter = 1
        self.total_time, *_ = hist.get_last_for_session(self.sid)
        self.all_quests = {}
        self.treeview = None

        self.board_frame = tk.Frame(self, bg='#0d232d')
        self.board_frame.place(relx=0, rely=0, relwidth=.66, relheight=1)

        self.quests_frame = tk.Frame(self, bg='light cyan')
        self.quests_frame.place(relx=.66, rely=0, relwidth=.34, relheight=.85)

        self.controls_frame = tk.Frame(self, bg='lemon chiffon')
        self.controls_frame.place(relx=.66, rely=.85, relwidth=.34, relheight=.15)

        self.populate_board_frame()
        self.populate_controls_frame()
        self.populate_quests_frame()
        self.get_history()

    def populate_board_frame(self):
        for i in range(1, 21):
            slot = Slot(self.board_frame, i, compound='left')
            slot.place(relx=i % 3 / 3, rely=i // 3 / 7, relwidth=1/3-.01, relheight=1/7-.01)
            self.slots.update({i: slot})

    def populate_controls_frame(self):
        _next = cw.Button(self.controls_frame, text='', command=self.next, font=(cw.FONT, 24))
        previous = cw.Button(self.controls_frame, text='', command=self.previous, font=(cw.FONT, 24))
        play = cw.Button(self.controls_frame, text='', command=self.previous, font=(cw.FONT, 24))
        play['command'] = lambda b=play: self.play(play)

        previous.pack(side='left', fill='both', expand=1)
        play.pack(side='left', fill='both', expand=1)
        _next.pack(side='left', fill='both', expand=1)

    def populate_quests_frame(self):
        style = self.parent.style.create_tv_style('quests', font=(cw.FONT, 10), rowheight=40,
                                                  heading_bg='#363636', heading_font=(cw.FONT, 14, 'bold'))
        self.treeview = treeview = cw.TreeView(self.quests_frame, show='tree', columns=('data', 'quantity'),
                                               style=style)
        self.treeview.pack(fill='both', expand=1)

        treeview.heading('#0', anchor='w', text='')
        treeview.heading('data', anchor='w', text='Data')
        treeview.heading('quantity', anchor='w', text='q')

        treeview.column('#0', minwidth=0, width=0, stretch=0, anchor='w')
        treeview.column('data', minwidth=305-20, width=305-20, stretch=0, anchor='w')
        treeview.column('quantity', minwidth=20, width=20, stretch=0, anchor='w')

    def get_history(self):
        history = hist.get_history_by_sid(self.sid)

        for _, deltatime, identifier, slot, value in history:
            result = self.slots[slot].insert(deltatime, identifier, value)
            if result is not None:
                dtime, qid = result
                try:
                    self.all_quests[qid].append(dtime)
                except KeyError:
                    self.all_quests.update({qid: [dtime]})

        self.treeview_insert()
        [slot.next() for slot in self.slots.values()]

    def treeview_insert(self):
        print(len(self.all_quests))
        for qid, times in self.all_quests.items():

            children = self.treeview.get_children()

            if qid in children:
                value = str(datetime.datetime.fromtimestamp('dtime' + self.parent.start))

            else:
                value = f'+{db.get_quest_points(qid)}, {db.get_quest_name_from_qid(qid)}'
                self.treeview.insert('', 'end', values=(value, f'x{len(times)}'))

    def next(self):
        # print(button.cget('text'))
        slot = None
        lowest = None

        for s in self.slots.values():
            current = s.get_next()
            if current is not None:
                if lowest is None or lowest > current[0]:
                    lowest = current[0]
                    slot = s

        try:
            slot.current += 1
            slot.update()
            return True
        except AttributeError:
            pass
        return False

    def previous(self):
        slot = None
        lowest = None

        for s in self.slots.values():
            current = s.get_previous()
            if current is not None:
                if lowest is None or lowest < current[0]:
                    lowest = current[0]
                    slot = s

        try:
            slot.current -= 1
            slot.update()
        except AttributeError:
            pass

    def play(self, button):
        button.configure(text='', command=lambda b=button: self.pause(b))

        for slot in self.slots.values():
            slot.autoplay()

    def pause(self, button):
        button.configure(text='', command=lambda b=button: self.play(b))

        for slot in self.slots.values():
            slot.after_cancel(slot.after_schedule)


class ChooseGUI(top):
    def __init__(self, parent=None):
        self.parent = parent
        super(ChooseGUI, self).__init__(parent)
        self.geometry('850x500+600+100')
        self.config(bg='#666666')
        self.resizable(0, 0)

        self.style = cw.CustomStyle(self.parent)

        self.treeview = None
        self.create_treeview()

        self.remove_button = cw.Button(self, text=local['delete_history'], fg=cw.REMOVE_RED, bg='#2d2121',
                                       command=self.remove_selected)
        self.remove_button.place(x=0, rely=.9, width=348, relheight=.1)

        self.summaries = SessionSummary(self, bg='red')
        self.summaries.place(x=350, rely=0, width=500, relheight=1)

        self.populate_treeview()
        self.listener()

    def create_treeview(self):
        style = self.style.create_tv_style('history', font=(cw.FONT, 12), rowheight=30, heading_bg='#363636',
                                           heading_font=(cw.FONT, 14, 'bold'))
        self.treeview = treeview = cw.TreeView(self, columns=('name', 'date', 'time'), style=style)
        treeview.place(relx=0, rely=0, width=348, relheight=.9)

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
            self.treeview.insert('', 'end', sid, values=(name, f'{timestamp:%d/%m/%Y}', f'{timestamp:%H:%M:%S}'))

    def listener(self):
        # print(self.summaries.sid)
        sid = self.treeview.selection()
        if sid:
            sid = sid[0]
            if self.summaries.sid != sid:
                self.summaries.sid = sid
        self.after(50, self.listener)

    def remove_selected(self):
        sid = self.treeview.selection()
        if sid:
            hist.delete_session(sid[0])

            self.treeview.delete(*self.treeview.get_children())
            self.populate_treeview()


class SessionSummary(tk.Frame):
    def __init__(self, parent, **kw):
        self.parent = parent
        super(SessionSummary, self).__init__(parent, **kw)

        self._selected = None
        self._sid = None
        self.scrollframe = None
        self.found = None
        self.selected_imgs = []
        self.sel_label_var = tk.StringVar(self)
        self.sel_name_var = tk.StringVar(self)
        self.sel_req_var = tk.StringVar(self)

        self.found_label_var = tk.StringVar(self)
        self.time_label_var = tk.StringVar(self)
        self.count_label_var = tk.StringVar(self)

        self.selected_frame = tk.Frame(self, bg='pink')
        self.selected_frame.place(relx=0, rely=0, width=500, height=245)

        self.summary_frame = tk.Frame(self, bg='cyan')
        self.summary_frame.place(relx=0, y=245, width=500, height=255)

        self.populate_selected_frame()
        self.populate_summary_frame()

    def populate_selected_frame(self):
        label = Label(self.selected_frame, bg=cw.HEADING_BG, fg=cw.MAIN_FG, textvariable=self.sel_label_var,
                      font=(cw.FONT, 13, 'bold'))
        label.pack(fill='x')

        frame = tk.Frame(self.selected_frame, bg='black')
        frame.pack(fill='both', expand=1)

        self.scrollframe = cw.ScrollFrame(frame, bg=cw.DARK_BLUE)
        self.scrollframe.bind_scroll(self.parent)
        self.scrollframe.place(relx=0, rely=0, relwidth=1, relheight=.8)

        details_frame = tk.Frame(frame, bg='light cyan')
        details_frame.place(relx=0, rely=.8, relwidth=1, relheight=.2)
        self.update_idletasks()

        name_label = Label(details_frame, textvariable=self.sel_name_var, wraplength=500, bg=cw.DARK_BLUE,
                           fg=cw.MAIN_FG)
        name_label.pack(side='left', fill='both', expand=1)

        req_label = Label(details_frame, textvariable=self.sel_req_var, compound='left', wraplength=150,
                          bg=cw.DARK_BLUE, fg=cw.MAIN_FG)
        req_label.pack(side='left', fill='both', expand=1)

    def populate_summary_frame(self):
        labels = (['found_quest', self.found_label_var], ['time_taken', self.time_label_var])

        for string, var in labels:
            frame = tk.Frame(self.summary_frame, bg='red')
            frame.pack(fill='both', expand=1)

            label = Label(frame, text=local[string]+': ', justify='left', bg='#0d232d')
            label.pack(side='left', fill='both')

            label = Label(frame, bg='#0d232d', textvariable=var, justify='left', anchor='w', fg=cw.SELECTED_YELLOW,
                          wraplength=300)
            label.pack(side='left', fill='both', expand=1, anchor='w')

        button = cw.Button(self.summary_frame, text='Ver Histórico',
                           command=lambda p=self.parent: History(self.sid, p))
        button.pack(fill='both', expand=1)

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, values: iter):
        self._selected = values
        # destroy previous widgets
        [widget.destroy() for widget in self.scrollframe.viewPort.grid_slaves()]

        cols = 6
        width = self.scrollframe.viewPort.winfo_width()/cols
        for n, qid in enumerate(values):
            self.scrollframe.viewPort.grid_columnconfigure(n % cols, minsize=width)

            _, _, points, *_, quest_icon, _ = db.get_quest_by_id(qid)

            bg, fg = (cw.DARK_BLUE, cw.MAIN_FG) if qid != self.found else (cw.SELECTED_YELLOW, cw.DARK_BLUE)

            img = ImageTk.PhotoImage(load_quest_image(quest_icon, width=width-10))
            label = Label(self.scrollframe.viewPort, compound='top', text=f'+{points}', image=img, bg=bg, fg=fg)
            label.grid(row=n // cols, column=n % cols, sticky='nswe')

            self.quest_hover(label, qid)
            label.image = img

        self.sel_label_var.set(f'{len(values)} missões selecionadas')

    def update_sel_labels(self, qid):
        _, name, _, req, *_ = db.get_quest_by_id(qid)
        self.sel_name_var.set(name)
        self.sel_req_var.set(f'0 / {req}')

    @property
    def sid(self):
        return self._sid

    @sid.setter
    def sid(self, v):
        self._sid = v
        session = hist.get_session_by_sid(self._sid)
        # history = hist.get_history_by_sid(self._sid)

        selected = [int(i) for i in str(session[-1]).split(',') if i]
        elapsed_time, identifier, value = hist.get_last_for_session(self._sid)

        self.found = value if identifier == 'q' and value in selected else None

        self.selected = selected

        self.time_label_var.set(time.strftime('%Hh %Mm %Ss', time.gmtime(elapsed_time)))
        self.found_label_var.set(db.get_quest_name_from_qid(self.found))

    def quest_hover(self, widget, num):
        fg = widget.cget('fg')
        bg = widget.cget('bg')

        def enter():
            widget.configure(bg=cw.ADD_GREEN, fg='#262626')
            self.update_sel_labels(num)

        def leave():
            widget.configure(fg=fg, bg=bg)
            self.sel_name_var.set('')
            self.sel_req_var.set('')

        widget.bind('<Enter>', lambda e: enter())
        widget.bind('<Leave>', lambda e: leave())


if __name__ == "__main__":
    ChooseGUI().mainloop()
