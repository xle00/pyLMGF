# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk

from databases import QuestDB, Pointers, LocalDB
import functions as funcs
import cwidgets as cw
from configs import load_configs


configs = load_configs()
db = QuestDB()
pointers = Pointers()
loc = LocalDB().get_main_localization()


class MainGUI(tk.Tk):
    def __init__(self):
        super(MainGUI, self).__init__()
        width, height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.width, self.height = width//2, height//2
        # self.geometry(f'{self.width}x{self.height}+{width//4}+{height//4}')
        # self.state('zoomed')
        self.geometry(f"1210x750+{1920//2-1210//2}+{1080//2-750//2}")
        self.minsize(850, 550)
        self['bg'] = '#444444'

        cw.CustomStyle(self)

        self.last_button = None

        self.icon_column_width = 70
        self.main_treeview = cw.TreeView(None)
        self.main_scrollbar = ttk.Scrollbar(None)
        self.focused_item = None

        self.sel_treeview = cw.TreeView(None)
        self.focused_sel = None

        spacing = 0.0025
        cat_f = {'x': 0, 'y': 0, 'w': 1, 'h': 0.03880597015}
        mtv_f = {'x': 0, 'y': cat_f['h'], 'w': 0.7438016529, 'h': 0.6119402985}
        stv_f = {'x': 0, 'y': mtv_f['h'] + cat_f['h'], 'w': mtv_f['w']/2, 'h': 1 - mtv_f['h'] - cat_f['h']}
        df1_f = {'x': mtv_f['w'], 'y': mtv_f['y'], 'w': 1-mtv_f['w'], 'h': mtv_f['h']}
        df2_f = {'x': stv_f['w'], 'y': stv_f['y'], 'w': stv_f['w'], 'h': stv_f['h']}
        but_f = {'x': df1_f['x'], 'y': df2_f['y'], 'w': df1_f['w'], 'h': df2_f['h']}

        self.cat_frame = tk.Frame(self, bg='#888888')
        self.cat_frame.place(relx=cat_f['x'], rely=cat_f['y'], relwidth=cat_f['w'], relheight=cat_f['h'])

        self.treeview_frame = tk.Frame(self, bg='yellow')
        self.treeview_frame.place(relx=mtv_f['x'], rely=mtv_f['y'], relwidth=mtv_f['w'], relheight=mtv_f['h']-spacing)

        self.selected_quests_frame = tk.Frame(self, bg='blue')
        self.selected_quests_frame.place(relx=stv_f['x'], rely=stv_f['y'], relwidth=stv_f['w'], relheight=stv_f['h'])

        self.details_frame2 = tk.Frame(self, bg='purple')
        self.details_frame2.place(relx=df2_f['x'], rely=df2_f['y'], relwidth=df2_f['w']-spacing/2, relheight=df2_f['h'])

        self.buttons_frame = tk.Frame(self, bg='orange')
        self.buttons_frame.place(relx=but_f['x'], rely=but_f['y'], relwidth=but_f['w'], relheight=but_f['h'])

        self.details_frame1 = tk.Frame(self, bg='cyan')
        self.details_frame1.place(relx=df1_f['x'], rely=df1_f['y'], relwidth=df1_f['w'], relheight=df1_f['h']-spacing)

        self.populate_tab_frame()
        self.populate_treeview_frame()
        self.populate_sel_treeview_frame()
        self.populate_buttons_frame()
        self.populate_details_frame1()
        self.populate_details_frame2()
        self.change_listener()

        self.last_item = None
        self.bind_events()

        self.bind('<Configure>', lambda e: self.readjust(e))
        self.readjust()

    def bind_events(self):
        ms = 10

        def release():
            self.main_treeview.selection_remove(*self.main_treeview.get_children())
            self.main_treeview.focus('')

        def mouse_wrapper(func):
            def inner(event):
                widget = event.widget
                x, y = event.x, event.y
                item = widget.identify_row(y)
                return func(widget, item)
            return inner

        @mouse_wrapper
        def left_click(widget, item):
            if not item.isdecimal():
                if widget.item(item)['open']:
                    widget.item(item, open=0)
                else:
                    widget.item(item, open=1)

            if self.group:
                self.after(ms, release)

        @mouse_wrapper
        def right_click(widget, item):
            if item.isdecimal():
                widget.selection_remove(item)

        @mouse_wrapper
        def left_drag(widget, item):
            widget.selection_set(item)
            widget.focus(item)

        @mouse_wrapper
        def right_drag(widget, item):
            if item in widget.selection():
                widget.selection_remove(item)
                widget.focus(item)
            if self.group:
                self.after(ms, release)

        @mouse_wrapper
        def middle_drag(widget, item):
            if item not in widget.selection():
                widget.selection_add(item)
                widget.focus(item)
            if self.group:
                self.after(ms, release)

        @mouse_wrapper
        def double_left(widget, item):
            if widget is self.main_treeview:
                if item in self.sel_treeview.get_children():
                    self.remove_from_selected([item])
                else:
                    if item.isdecimal():
                        self.add_to_selected()
            elif widget is self.sel_treeview:
                self.remove_from_selected()

        def keyboard_wrapper(func):
            def inner(event):
                widget = event.widget
                return func(widget)
            return inner

        @keyboard_wrapper
        def add(widget):
            self.add_to_selected()

        @keyboard_wrapper
        def remove_from_main(widget):
            self.remove_from_selected(widget.selection())

        @keyboard_wrapper
        def remove(widget):
            self.remove_from_selected()

        @keyboard_wrapper
        def select_all(widget):
            widget.selection_set(*widget.get_children())

        @keyboard_wrapper
        def deselect_all(widget):
            widget.selection_remove(*widget.get_children())

        self.main_treeview.bind('<Button-1>', left_click)
        self.main_treeview.bind('<Button-2>', left_click)
        self.main_treeview.bind('<Button-3>', right_click)
        self.main_treeview.bind('<B1-Motion>', left_drag)
        self.main_treeview.bind('<B2-Motion>', middle_drag)
        self.main_treeview.bind('<B3-Motion>', right_drag)
        self.main_treeview.bind('<Double-Button-1>', double_left)
        self.main_treeview.bind('<space>', add)
        self.main_treeview.bind('<Return>', add)
        self.main_treeview.bind('<Delete>', remove_from_main)
        self.main_treeview.bind('<Escape>', deselect_all)
        self.main_treeview.bind('<Control-a>', select_all)
        self.main_treeview.bind('<Control-A>', select_all)
        self.main_treeview.bind('<Control-d>', deselect_all)
        self.main_treeview.bind('<Control-D>', deselect_all)

        self.sel_treeview.bind('<Button-3>', right_click)
        self.sel_treeview.bind('<B1-Motion>', left_drag)
        self.sel_treeview.bind('<B2-Motion>', middle_drag)
        self.sel_treeview.bind('<B3-Motion>', right_drag)
        self.sel_treeview.bind('<Double-Button-1>', double_left)
        self.sel_treeview.bind('<Delete>', remove)
        self.sel_treeview.bind('<space>', remove)
        self.sel_treeview.bind('<Return>', remove)
        self.sel_treeview.bind('<Escape>', deselect_all)
        self.sel_treeview.bind('<Control-a>', select_all)
        self.sel_treeview.bind('<Control-A>', select_all)
        self.sel_treeview.bind('<Control-d>', deselect_all)
        self.sel_treeview.bind('<Control-D>', deselect_all)

    def populate_tab_frame(self):
        for tab in db.get_categories():
            button = cw.Button(self.cat_frame, text=tab, font=(cw.font, 12, 'normal'))
            button['command'] = lambda t=tab, b=button: self.tab_button_command(t, b)
            button.pack(side='left', fill='both', expand=1, pady=(0, 2))

    def populate_treeview_frame(self):
        frame = tk.Frame(self.treeview_frame, bg='#262626')
        frame.place(relx=0, rely=0, relwidth=1, relheight=.9)

        self.main_scrollbar = scrollbar = tk.Scrollbar(frame, orient='vertical',)

        treeview = self.main_treeview = cw.TreeView(frame, displaycolumns='#all', height=8, show='tree',
                                                    yscrollcommand=scrollbar.set, style='treeview.Treeview',
                                                    padding=10)
        treeview['columns'] = ('Name', 'Points')
        treeview.pack(side='left', fill='both', expand=1)

        scrollbar['command'] = self.main_treeview.yview

        button = cw.Button(self.treeview_frame, text=loc['add_quest'], command=self.add_to_selected, fg=cw.ADD_GREEN,
                           bg='#1d2d2a', relief='flat', font=(cw.font, 13, 'bold'))
        button.place(relx=0, rely=.9, relwidth=1, relheight=.1)

        treeview.heading('#0', anchor='w', text='')
        treeview.heading('Name', anchor='w', text=loc['quest'])
        treeview.heading('Points', anchor='w', text=loc['points'])

        treeview.column('#0', minwidth=self.icon_column_width, width=self.icon_column_width, stretch=0, anchor='w')
        treeview.column('Name', minwidth=700, width=700, stretch=1, anchor='w')
        treeview.column('Points', minwidth=112, width=112, stretch=1, anchor='w')

        treeview.tag_configure('normal', background=cw.TV_BG, foreground=cw.ALT_FG, font=(cw.font, 14, 'normal'))
        treeview.tag_configure('selected', background='#d1ae62', foreground='#262626', font=(cw.font, 14, 'bold'))
        treeview.tag_configure('parent', background='#3a5763', foreground=cw.ALT_FG, font=(cw.font, 15, 'bold',))

    def populate_sel_treeview_frame(self):
        frame = tk.Frame(self.selected_quests_frame, bg='#262626')
        frame.place(relx=0, rely=0, relwidth=1, relheight=.85)

        treeview = self.sel_treeview = cw.TreeView(frame, style='sectreeview.Treeview',
                                                   height=6, padding=(0, 5, 0))
        treeview.configure(columns=('Name', 'Points'))
        treeview.pack(side='left', fill='both', expand=1)

        treeview.heading('#0', anchor='center', text='')
        treeview.heading('Name', anchor='center', text=loc['quest'])
        treeview.heading('Points', anchor='center', text=loc['points'])

        treeview.column('#0', minwidth=0, width=0, stretch=0, anchor='center')
        treeview.column('Name', minwidth=380, width=380, stretch=1, anchor='center')
        treeview.column('Points', minwidth=70, width=70, stretch=1, anchor='center')

        button = cw.Button(self.selected_quests_frame, text=loc['remove_quest'], command=self.remove_from_selected,
                           fg=cw.REMOVE_RED, bg='#2d2121')
        button.place(relx=0, rely=.85, relheight=.15, relwidth=1)

        treeview.tag_configure('normal', background='#222222', foreground='#d0d0d0')

        for qid in db.get_selected_ids():
            _, name, points, *_ = db.get_quest_by_id(qid)
            treeview.insert('', 'end', qid, values=(name, f'+{points}'), tags=('normal',))

        self.update_sel_headings()

    def populate_buttons_frame(self):
        buttons = [[loc['pointers'], 'call_pointers'], [loc['history'], 'call_history'], [loc['start'], 'call_start']]
        for text, command in buttons:
            button = cw.Button(self.buttons_frame, text=text, command=getattr(self, command, None),
                               font=(cw.font, 18, 'bold'), bg='#262626')
            button.pack(fill='both', expand=1)

    def populate_details_frame1(self):
        name_label = cw.Label(self.details_frame1, compound='top', wraplength=300, fg=cw.YELLOW)
        name_label.pack(fill='both', expand=1)

        points_label = cw.Label(self.details_frame1, compound='left')
        points_label.pack(fill='both', expand=1)

        req_label = cw.Label(self.details_frame1, compound='left')
        req_label.pack(fill='both', expand=1)

        time_label = cw.Label(self.details_frame1, compound='left')
        time_label.pack(fill='both', expand=1)

    def populate_details_frame2(self):
        name_label = cw.Label(self.details_frame2, compound='left', wraplength=300, fg=cw.YELLOW)
        name_label.pack(fill='both', expand=1)

        frame = tk.Frame(self.details_frame2)
        frame.pack(fill='both', expand=1)

        points_label = cw.Label(frame, compound='top')
        points_label.pack(fill='both', expand=1, side='left')

        req_label = cw.Label(frame, compound='top')
        req_label.pack(fill='both', expand=1, side='left')

        time_label = cw.Label(frame, compound='top')
        time_label.pack(fill='both', expand=1, side='left')

    def populate_main_treeview(self, category):
        self.group = group = configs['group']

        self.main_treeview.delete(*self.main_treeview.get_children())
        quests = db.get_quests_by_category(category)

        names = []

        self.main_treeview.loaded_imgs = {}
        img_height = 44

        for quest_id, name, points, req, time, *_, selected, _, q_img, _ in quests:
            img_hash = f'{q_img}_{img_height}'

            if img_hash in self.main_treeview.loaded_imgs.keys():
                img = self.main_treeview.loaded_imgs.get(img_hash)
            else:
                img = funcs.load_quest_image(q_img, img_height)
                img = ImageTk.PhotoImage(img)
                self.main_treeview.loaded_imgs.update({img_hash: img})

            tags = ('selected',) if selected else ('normal',)

            if group:
                nameid = name.split(':')[0] if ':' in name else name

                if nameid not in names:
                    self.main_treeview.insert('', 'end', nameid, values=(nameid,), image=img, tags='parent')
                    names.append(nameid)

                self.main_treeview.insert(nameid, 'end', iid=quest_id, values=(name, f'+{points}'), tags=tags)
            else:
                self.main_treeview.insert('', 'end', iid=quest_id, values=(name, f'+{points}'), image=img,
                                          tags=tags)

        self.resize_main_treeview()

    def add_to_selected(self):
        selected = self.get_selected_from_main()
        # print(selected)
        if not selected:
            return
        db.set_selected([d['Id'] for d in selected])

        for quest in selected:
            iid = quest['Id']
            name = quest['Name']
            points = quest['Points']
            if iid not in self.sel_treeview.get_children():
                self.sel_treeview.insert('', 'end', iid=iid, values=(name, points), tags=('normal',))

        # update selected colors
        for qid in self.main_treeview.selection():
            if qid.isdecimal():
                self.main_treeview.item(qid, tags=('selected',))

        self.update_sel_headings()

    def remove_from_selected(self, qid=None):
        if qid:
            selected = [q for q in qid if q in self.sel_treeview.get_children()]
        else:
            selected = self.sel_treeview.selection()
            if not selected:
                return

        # delete from rows from treeview and set quests unselected
        self.sel_treeview.delete(*selected)
        db.set_unselected(selected)

        # update selected colors
        if not self.group:
            [self.main_treeview.item(qid, tags=('selected',)) if qid in self.sel_treeview.get_children() else
                self.main_treeview.item(qid, tags=('normal',)) for qid in self.main_treeview.get_children()]
        else:
            [self.main_treeview.item(qid, tags=('selected',)) if qid in self.sel_treeview.get_children() else
                self.main_treeview.item(qid, tags=('normal',))
                for parent in self.main_treeview.get_children() for qid in self.main_treeview.get_children(parent)]

        self.update_sel_headings()

    def update_sel_headings(self):
        lenght = len(self.sel_treeview.get_children())
        name_text = f'{lenght} {loc["quest"]}' if lenght == 1 else f'{lenght} {loc["quests"]}'
        points = [int(self.sel_treeview.item(item)['values'][1]) for item in self.sel_treeview.get_children()]
        points_text = f'~{sum(points) // len(points)}' if len(points) else ''

        self.sel_treeview.heading('Name', text=name_text)
        self.sel_treeview.heading('Points', text=points_text)

    def tab_button_command(self, tab, button):
        cw.unbind_invert(button)

        if self.last_button:
            if button is self.last_button:
                return

            self.last_button.configure(bg=cw.BUTTON_BG, fg=cw.MAIN_FG)
            cw.bind_hover(self.last_button, bg=cw.BUTTON_BG_HOVER)

        button.configure(bg=cw.MAIN_FG, fg=cw.BUTTON_BG)
        self.last_button = button

        self.resize_tab_buttons(self.width)

        self.populate_main_treeview(tab)
        self.main_treeview.yview_moveto(0.0)

    def get_selected_from_main(self):
        tv = self.main_treeview
        selected = []
        for i in tv.selection():
            # print(i, i.isdecimal())
            if i.isdecimal():
                d = tv.set(i)
                d.update({'Id': i})
                selected.append(d)
        return selected

    def change_listener(self):
        qid = [i for i in self.main_treeview.selection() if i.isdecimal()]
        qid = qid[-1] if qid else ''

        if qid != self.focused_item:
            self.focused_item = qid
            self.refresh_details('main')

        '-------------------------------------------------------------------------------------------------------------'

        qid = self.sel_treeview.selection()
        qid = qid[-1] if qid else ''

        if qid != self.focused_sel:
            self.focused_sel = qid
            self.refresh_details('sel')

        self.after(100, self.change_listener)

    def refresh_details(self, which, resize=1.0):
        if which == 'main':
            name_label, points_label, req_label, time_label = self.details_frame1.children.values()
            _id = self.focused_item
            spacer = ' '
            bg = '#212121'
        elif which == 'sel':
            name_label, frame = self.details_frame2.children.values()
            points_label, req_label, time_label = frame.children.values()
            _id = self.focused_sel
            spacer = ''
            bg = '#212121'
        else:
            return

        if not _id:
            name_label.configure(image=None, text='', bg=bg)
            name_label.image = None

            points_label.configure(image=None, text='', bg=bg)
            points_label.image = None

            req_label.configure(image=None, text='', bg=bg)
            req_label.image = None

            time_label.configure(image=None, text='', bg=bg)
            time_label.image = None
        else:
            _, name, points, req, time, *_, quest_img, quest_icon = db.get_quest_by_id(_id)

            img = funcs.load_quest_image(quest_img, resize=resize)
            bg = funcs.get_most_common_color(img)
            r, g, b = [int(x, 16) for x in (bg[1:3], bg[3:5], bg[5:])]

            while (r+g+b)//3 > 45:
                r *= .9
                g *= .9
                b *= .9
            bg = f'#{hex((int(r)*256*256 + int(g)*256 + int(b)))[2:]:0>6}'

            name_img = ImageTk.PhotoImage(img, 2)
            points_img = ImageTk.PhotoImage(funcs.load_icon_image(66, height=40, resize=resize))
            req_img = ImageTk.PhotoImage(funcs.load_icon_image(quest_icon, height=40, resize=resize))
            time_img = ImageTk.PhotoImage(funcs.load_icon_image(11, height=40, resize=resize))

            name_label.configure(image=name_img, text=name, bg=bg)
            name_label.image = name_img

            points_label.configure(image=points_img, text=f'{spacer}+{points}', bg=bg)
            points_label.image = points_img

            req_label.configure(image=req_img, text=f'{spacer}0 / {req}', bg=bg)
            req_label.image = req_img

            time_label.configure(image=time_img, text=f'{spacer}{time}', bg=bg)
            time_label.image = time_img

    def readjust(self, event=None):
        if event is None:
            pass
        elif isinstance(event.widget, MainGUI):
            pass
        else:
            return

        # get root dimensions
        width, height = self.get_root_dimensions()

        if self.width == width and self.height == height:
            return

        # readjust widgets
        self.resize_tab_buttons(width)
        self.resize_main_treeview()
        self.resize_sel_treeview()
        self.resize_details1()
        self.resize_details2()

        self.width, self.height = width, height

    def get_root_dimensions(self):
        width, rest = self.geometry().split('x')
        height, *_ = rest.split('+')
        return int(width), int(height)

    def resize_tab_buttons(self, width):
        sizes = ([1700, 14], [1600, 13], [1500, 12], [1400, 11], [1300, 10], [1150, 9], [1050, 8], [1000, 7])
        buttons = self.cat_frame.children.values()

        for w, size in sizes[::-1]:
            if w >= width:
                for button in buttons:
                    if button is self.last_button:
                        button.configure(font=(cw.font, size, 'bold'))
                    else:
                        button.configure(font=(cw.font, size, 'normal'))
                break
        for w, size in sizes[::-1]:
            if w >= width:
                for button in buttons:
                    if button is self.last_button:
                        button.configure(font=(cw.font, size, 'bold'))
                    else:
                        button.configure(font=(cw.font, size, 'normal'))
                break
        else:
            for button in buttons:
                if button is self.last_button:
                    button.configure(font=(cw.font, sizes[0][1], 'bold'))
                else:
                    button.configure(font=(cw.font, sizes[0][1], 'normal'))

    def resize_main_treeview(self):
        button = [widget for widget in self.treeview_frame.children.values() if isinstance(widget, tk.Button)][0]
        treeview = self.main_treeview

        self.update_idletasks()
        req_width = button.winfo_width()
        req_height = treeview.winfo_height()

        # update scrollbar
        rows = sum([1 for _ in treeview.get_children()])
        rows_showed = req_height//45
        if rows > rows_showed:
            self.main_scrollbar.pack(side='right', fill='y')
        else:
            self.main_scrollbar.pack_forget()

        # resize columns
        column_1 = int((req_width-self.icon_column_width) * .87)
        column_2 = int((req_width-self.icon_column_width) * .13)
        treeview.column('Name', minwidth=column_1, width=column_1, stretch=0, anchor='w')
        treeview.column('Points', minwidth=column_2, width=column_2, stretch=0, anchor='w')

    def resize_sel_treeview(self):
        treeview = self.sel_treeview
        width = treeview.winfo_width()

        treeview.column('Name', minwidth=int(width*.85), width=int(width*.85), stretch=0, anchor='center')
        treeview.column('Points', minwidth=int(width*.15), width=int(width*.15), stretch=0, anchor='center')

    def resize_details1(self):
        frame = self.details_frame1
        children = list(frame.children.values())
        for c in children:
            self.update_idletasks()
            if self.main_treeview.focus():
                c.configure(wraplength=frame.winfo_width()-10)

        if frame.winfo_height() < frame.winfo_reqheight():
            self.update_idletasks()
            for c in children:
                if self.main_treeview.focus():
                    c.configure(font=(cw.font, 10, 'bold'))
            if self.main_treeview.focus():
                self.refresh_details('main', .8)
        else:
            self.update_idletasks()
            for c in children:
                if self.main_treeview.focus():
                    c.configure(font=(cw.font, 14, 'bold'))
            if self.main_treeview.focus():
                self.refresh_details('main', 1)

    def resize_details2(self):
        name, frame = self.details_frame2.children.values()
        if not name.cget('text'):
            return
        name.configure(wraplength=name.winfo_width() - 120 - 10)

        children = [name] + list(frame.children.values())

        if frame.winfo_height() < frame.winfo_reqheight():
            self.update_idletasks()
            for c in children:
                self.update_idletasks()
                c.configure(font=(cw.font, 10, 'bold'))
            self.refresh_details('sel', .8)
        else:
            self.update_idletasks()
            for c in children:
                self.update_idletasks()
                c.configure(font=(cw.font, 14, 'bold'))
            self.refresh_details('sel', 1)

    def call_start(self):
        from LMGF5 import main
        self.destroy()
        main()

    def call_pointers(self):
        import pointers_GUI
        pointers_GUI.ConfigGUI(self)

    def call_history(self):
        from hisory_gui import ChooseGUI
        ChooseGUI(self)


if __name__ == '__main__':
    gui = MainGUI().mainloop()
