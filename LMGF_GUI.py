# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from configs import QuestDB, Pointers

db = QuestDB()
pointers = Pointers()


FONT = '-family Gadugi -weight bold '
YELLOW = '#f7e083'
MAIN_FG = '#efeee9'
REMOVE_RED = '#e26161'
ADD_GREEN = '#61e261'
BUTTON_BG = '#091f26'
font = 'Gadugi'


def invert_on_hover(widget: tk.Widget):
    fg = widget.cget('fg')
    bg = widget.cget('bg')

    widget.bind('<Enter>', lambda e: widget.configure(fg=bg, bg=fg))
    widget.bind('<Leave>', lambda e: widget.configure(fg=fg, bg=bg))


def unbind_invert(widget: tk.Widget):
    widget.bind('<Enter>', lambda e: None)
    widget.bind('<Leave>', lambda e: None)


def bind_hover(widget: tk.Widget, **kw):
    fg = widget.cget('fg')
    bg = widget.cget('bg')

    widget.bind('<Enter>', lambda e: widget.configure(**kw))
    widget.bind('<Leave>', lambda e: widget.configure(fg=fg, bg=bg))


def load_quest_image(img_index, height=None, width=None, resize=1.0):
    path = f'imgs\\quests\\{int(img_index):03d}.png'
    img = Image.open(path)

    if height:
        ratio = img.height / (height*resize)
    elif width:
        ratio = img.width / (width*resize)
    else:
        return img
    new_dimensions = int(img.width // ratio), int(img.height // ratio)
    return img.resize(new_dimensions)


def load_icon_image(img_index, height=None, width=None, resize=1.0):
    img_index = 35 if not img_index else img_index
    path = f'imgs\\icons\\{int(img_index):03d}.png'
    img = Image.open(path)

    if height:
        ratio = img.height / (height*resize)
    elif width:
        ratio = img.width / (width*resize)
    else:
        return img
    new_dimensions = int(img.width // ratio), int(img.height // ratio)
    return img.resize(new_dimensions)


def get_img_color_avg(img):
    sum_r, sum_b, sum_g = 0, 0, 0
    count = 0
    for r, g, b in img.getdata():
        sum_r += r
        sum_g += g
        sum_b += b
        count += 1

    sum_r //= count
    sum_g //= count
    sum_b //= count

    return f'#{hex(sum_r*255*255 + sum_g*255 + sum_b)[2:]:0>6}'


def get_most_common_color(img, border_width=1):
    colors = {}
    color = 0
    width = img.width
    height = img.height
    for n, pixels in enumerate(img.getdata()):
        x, y = n % width, n // height
        if y < border_width or y >= width - border_width or x < border_width or x >= height - border_width:
            r, g, b = pixels
            c = r*256*256 + g*256 + b
            try:
                colors[c] += 1
            except KeyError:
                colors.update({c: 1})

    for c in sorted(colors.items(), key=lambda i: i[1], reverse=True):
        color = c[0]

        return f'#{hex(color)[2:]:0>6}'


class Button(tk.Button):
    def __init__(self, parent, **kw):
        super(Button, self).__init__(parent)
        self.configure(
            bg='#262626',
            fg=MAIN_FG,
            relief='flat',
            font=FONT + '-weight bold ',
            anchor='center',
            cursor='hand2',
        )
        self.config(**kw)
        bind_hover(self, bg='#565656')


class TreeView(ttk.Treeview):
    def __init__(self, parent, **kw):
        super(TreeView, self).__init__(parent, **kw)
        self.loaded_imgs = {}
        self.configure(
            selectmode='extended',
        )
        # print(self.keys())


class CustomStyle(ttk.Style):
    def __init__(self, parent):
        super(CustomStyle, self).__init__(parent)
        self.main_treeview_style()
        self.sec_treeview_style()

    def main_treeview_style(self):
        # heading layout
        self.element_create("Custom.Treeheading.border", "from", "default")
        self.layout("treeview.Treeview.Heading",
                    [("Custom.Treeheading.cell", {'sticky': 'nsew'}),
                     ("Custom.Treeheading.border", {'sticky': 'nswe', 'children':
                         [("Custom.Treeheading.padding", {'sticky': 'nswe', 'children':
                             [("Custom.Treeheading.image", {'side': 'right','sticky': ''}),
                              ("Custom.Treeheading.text", {'sticky': 'we'})]})]}),])

        # heading style
        self.configure("treeview.Treeview.Heading",
                       font=('Gadugi', 18, 'bold'),
                       background='black',
                       foreground='white'
                       )

        # heading map
        self.map("treeview.Treeview.Heading",
                 relief=[('active', 'groove'), ('pressed', 'sunken')],
                 background=[('active', 'white')],
                 foreground=[('active', 'black')])
        # print(self.map('treeview.Treeview.Heading'))

        # style
        self.configure("treeview.Treeview",
                       highlightthickness=0,
                       bd=0,
                       font=('Gadugi', 14),
                       rowheight=45,
                       background='#262626',
                       )

        # layout
        self.layout("treeview.Treeview", [
             ('treeview.Treeview.treearea', {'sticky': 'news'})])

        # map
        self.map('treeview.Treeview',
                 background=[('disabled', '#262626'), ('selected', MAIN_FG)],
                 foreground=[('disabled', MAIN_FG), ('selected', '#262626')],
                 relief=[('selected', 'flat')]
                 )

    def sec_treeview_style(self):
        # heading layout
        self.element_create("Custom2.Treeheading.border", "from", "default")
        self.layout("sectreeview.Treeview.Heading",
                    [("Custom2.Treeheading.cell", {'sticky': 'nsew'}),
                     ("Custom2.Treeheading.border", {'sticky': 'nswe', 'children':
                         [("Custom2.Treeheading.padding", {'sticky': 'nswe', 'children':
                             [("Custom2.Treeheading.image", {'side': 'right','sticky': ''}),
                              ("Custom2.Treeheading.text", {'sticky': 'we'})]})]}),])

        # heading style
        self.configure("sectreeview.Treeview.Heading",
                       font=('Gadugi', 12, 'bold'),
                       background='black',
                       foreground='white'
                       )

        # heading map
        self.map("sectreeview.Treeview.Heading",
                 relief=[('active', 'groove'), ('pressed', 'sunken')],
                 background=[('active', 'white')],
                 foreground=[('active', 'black')])

        # style
        self.configure("sectreeview.Treeview",
                       highlightthickness=0,
                       bd=0,
                       font=('Gadugi', 10),
                       background='#292929',
                       rowheight=25
                       )

        # layout
        self.layout("sectreeview.Treeview", [
            ('sectreeview.Treeview.treearea', {'sticky': 'news'})])

        print(self.map('Treeview'))

        # map
        self.map('sectreeview.Treeview',
                 background=[('disabled', '#262626'), ('selected', MAIN_FG)],
                 foreground=[('disabled', MAIN_FG), ('selected', '#262626')],
                 )


class Label(tk.Label):
    def __init__(self, parent, **kw):
        super(Label, self).__init__(parent)
        self.configure(
            bg='pink',
            fg=MAIN_FG,
            font=FONT+' -size 16',
        )
        self.config(**kw)


class MainGUI(tk.Tk):
    def __init__(self):
        super(MainGUI, self).__init__()
        width, height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.width, self.height = width//2, height//2
        self.geometry(f'{self.width}x{self.height}+{width//4}+{height//4}')
        self.minsize(850, 550)

        CustomStyle(self)

        self.last_button = None
        self.tab_button_font = ['Gadugi', 12, 'normal']

        self.icon_column_width = 70
        self.main_treeview = TreeView(None)
        self.main_scrollbar = ttk.Scrollbar(None)
        self.focused_item = None

        self.sel_treeview = TreeView(None)
        self.focused_sel = None

        self.tabs_frame = tk.Frame(bg='red')
        self.tabs_frame.place(relx=0, rely=0, relwidth=1, relheight=0.03880597015)

        self.treeview_frame = tk.Frame(bg='yellow')
        self.treeview_frame.place(relx=0, rely=0.03880597015, relwidth=0.7438016529, relheight=0.6119402985)

        self.selected_quests_frame = tk.Frame(bg='blue')
        self.selected_quests_frame.place(relx=0, rely=0.6507462687, relwidth=0.3719008264, relheight=0.3492537313)

        self.details_frame2 = tk.Frame(bg='purple')
        self.details_frame2.place(relx=0.3719008264, rely=0.6507462687, relwidth=0.3719008264, relheight=0.3492537313)

        self.buttons_frame = tk.Frame(bg='orange')
        self.buttons_frame.place(relx=0.7438016529, rely=0.6507462687, relwidth=0.2561983471, relheight=0.3492537313)

        self.details_frame1 = tk.Frame(bg='cyan')
        self.details_frame1.place(relx=0.7438016529, rely=0.03880597015, relwidth=0.2561983471, relheight=0.6119402985)

        self.populate_tab_frame()
        self.populate_treeview_frame()
        self.populate_sel_treeview_frame()
        self.populate_buttons_frame()
        self.populate_details_frame1()
        self.populate_details_frame2()
        self.change_listener()

        self.main_treeview.bind('<Return>', lambda e:  self.add_to_selected())
        self.main_treeview.bind('<space>', lambda e: self.add_to_selected())
        self.main_treeview.bind('<Double-Button-1>', lambda e: self.add_to_selected())
        self.main_treeview.bind('<B1-Motion>', lambda e, t=self.main_treeview: self.dragging(e, t))
        self.sel_treeview.bind('<Double-Button-3>', lambda e: 1)

        self.sel_treeview.bind('<B1-Motion>', lambda e, t=self.sel_treeview: self.dragging(e, t))
        self.sel_treeview.bind('<Delete>', lambda e: self.remove_from_selected())

        self.bind('<Configure>', lambda e: self.readjust(e))
        self.readjust()

    def populate_tab_frame(self):
        for tab in db.get_categories():
            button = Button(self.tabs_frame, text=tab, font=self.tab_button_font)
            button['command'] = lambda t=tab, b=button: self.tab_button_command(t, b)
            button.pack(side='left', fill='both', expand=1)

    def populate_treeview_frame(self):
        frame = tk.Frame(self.treeview_frame, bg='#262626')
        frame.place(relx=0, rely=0, relwidth=1, relheight=.9)

        self.main_scrollbar = scrollbar = tk.Scrollbar(frame, orient='vertical',)

        treeview = self.main_treeview = TreeView(frame, displaycolumns='#all', height=8, show='tree',
                                                 yscrollcommand=scrollbar.set, style='treeview.Treeview')
        treeview['columns'] = ('Name', 'Points')
        treeview.pack(side='left', fill='both', expand=1)

        scrollbar['command'] = self.main_treeview.yview

        button = Button(self.treeview_frame, text='Adicionar Missão', command=self.add_to_selected, fg=ADD_GREEN,
                        height=10)
        button.place(relx=0, rely=.9, relwidth=1, relheight=.1)

        treeview.heading('#0', anchor='w', text='')
        treeview.heading('Name', anchor='w', text='Missão')
        treeview.heading('Points', anchor='w', text='Pontos')

        treeview.column('#0', minwidth=self.icon_column_width, width=self.icon_column_width, stretch=0, anchor='w')
        treeview.column('Name', minwidth=700, width=700, stretch=0, anchor='w')
        treeview.column('Points', minwidth=112, width=112, stretch=0, anchor='w')

    def populate_sel_treeview_frame(self):
        treeview = self.sel_treeview = TreeView(self.selected_quests_frame, style='sectreeview.Treeview',
                                                height=6, show='tree', padding=(0,5,0))
        treeview.configure(columns=('Name', 'Points'))
        treeview.place(relx=0, rely=0, relheight=.85, relwidth=1)#.pack(fill='both', expand=1)

        treeview.heading('#0', anchor='center', text='')
        treeview.heading('Name', anchor='center', text='Missão')
        treeview.heading('Points', anchor='center', text='Pontos')

        treeview.column('#0', minwidth=0, width=0, stretch=0, anchor='center')
        treeview.column('Name', minwidth=380, width=380, stretch=0, anchor='center')
        treeview.column('Points', minwidth=70, width=70, stretch=0, anchor='center')

        button = Button(self.selected_quests_frame, text='Remover Missão', command=self.remove_from_selected,
                        fg=REMOVE_RED)
        button.place(relx=0, rely=.85, relheight=.15, relwidth=1)#pack(fill='both')

        treeview.tag_configure('normal', background='#262626', foreground='#d0d0d0')

        for qid in db.get_selected_ids():
            _, name, points, *_ = db.get_quest_by_id(qid)
            treeview.insert('', 'end', qid, values=(name, f'+{points}'), tags=('normal',))

    def populate_buttons_frame(self):
        buttons = [['Ponteiros', 'call_pointers'], ['Começar', 'call_start'],]
        for text, command in buttons:
            button = Button(self.buttons_frame, text=text, command=getattr(self, command, None),
                            font=FONT + '-size 18')
            button.pack(fill='both', expand=1)

    def populate_details_frame1(self):
        name_label = Label(self.details_frame1, compound='top', wraplength=300, fg=YELLOW)
        name_label.pack(fill='both', expand=1)

        points_label = Label(self.details_frame1, compound='left')
        points_label.pack(fill='both', expand=1)

        req_label = Label(self.details_frame1, compound='left')
        req_label.pack(fill='both', expand=1)

        time_label = Label(self.details_frame1, compound='left')
        time_label.pack(fill='both', expand=1)

    def populate_details_frame2(self):
        name_label = Label(self.details_frame2, compound='left', wraplength=300, fg=YELLOW)
        name_label.pack(fill='both', expand=1)

        frame = tk.Frame(self.details_frame2)
        frame.pack(fill='both', expand=1)

        points_label = Label(frame, compound='top')
        points_label.pack(fill='both', expand=1, side='left')

        req_label = Label(frame, compound='top')
        req_label.pack(fill='both', expand=1, side='left')

        time_label = Label(frame, compound='top')
        time_label.pack(fill='both', expand=1, side='left')

    def populate_main_treeview(self, category):
        self.main_treeview.delete(*self.main_treeview.get_children())
        quests = db.get_quests_by_category(category)

        self.main_treeview.loaded_imgs = {}
        img_height = 44
        for quest_id, name, points, *_, selected, _, q_img, _ in quests:
            img_hash = f'{q_img}_{img_height}'

            if img_hash in self.main_treeview.loaded_imgs.keys():
                img = self.main_treeview.loaded_imgs.get(img_hash)
            else:
                img = load_quest_image(q_img, img_height)
                img = ImageTk.PhotoImage(img)
                self.main_treeview.loaded_imgs.update({img_hash: img})

            tags = ('selected',) if selected else ('normal',)

            self.main_treeview.insert('', 'end', iid=quest_id, values=(name, f'+{points}'), image=img, tags=tags)
            self.main_treeview.tag_configure('normal', background='#262626', foreground='#d0d0d0', )
            self.main_treeview.tag_configure('selected', background='#d1ae62', foreground='#262626', )

        self.resize_main_treeview()

    def add_to_selected(self):
        selected = self.get_selected_from_main()
        if not selected:
            return
        db.set_selected([d['Id'] for d in selected])

        for quest in selected:
            iid = quest['Id']
            name = quest['Name']
            points = quest['Points']
            if iid not in self.sel_treeview.get_children():
                self.sel_treeview.insert('', 'end', iid=iid, values=(name, points), tags=('normal',))

        # refresh main treeview to update selected colors
        q_id = self.main_treeview.selection()
        self.populate_main_treeview(self.last_button.cget('text'))
        self.main_treeview.selection_set(*q_id)
        self.main_treeview.focus(q_id[-1])

    def remove_from_selected(self, qid=None):
        if qid:
            selected = ''
        else:
            selected = self.sel_treeview.selection()
            if not selected:
                return

            # delete from rows from treeview and set quests unselected
            self.sel_treeview.delete(*selected)
            db.set_unselected(selected)

            # refresh main treeview to update selected colors
            q_id = self.main_treeview.selection()
            if self.last_button:
                self.populate_main_treeview(self.last_button.cget('text'))
            self.main_treeview.selection_set(*q_id)
            try:
                self.main_treeview.focus(q_id[-1])
            except IndexError:
                return

    def tab_button_command(self, tab, button):
        unbind_invert(button)

        if self.last_button:
            if button is self.last_button:
                return

            self.last_button.configure(bg='#262626', fg=MAIN_FG)
            bind_hover(self.last_button, bg='#565656')

        button.configure(bg=MAIN_FG, fg='#262626')
        self.last_button = button

        self.resize_tab_buttons(self.width)

        self.populate_main_treeview(tab)

    def get_selected_from_main(self):
        tv = self.main_treeview
        selected = []
        for i in tv.selection():
            d = tv.set(i)
            d.update({'Id': i})
            selected.append(d)
        return selected

    def change_listener(self):
        q_id = self.main_treeview.selection()
        q_id = q_id[-1] if q_id else ''

        if q_id != self.focused_item:
            self.focused_item = q_id
            self.refresh_details('main')

        '-------------------------------------------------------------------------------------------------------------'

        q_id = self.sel_treeview.selection()
        q_id = q_id[-1] if q_id else ''

        if q_id != self.focused_sel:
            self.focused_sel = q_id
            self.refresh_details('sel')

        self.after(100, self.change_listener)

    def refresh_details(self, which, resize=1.0):
        if which == 'main':
            name_label, points_label, req_label, time_label = self.details_frame1.children.values()
            _id = self.focused_item
            spacer = ' '
        elif which == 'sel':
            name_label, frame = self.details_frame2.children.values()
            points_label, req_label, time_label = frame.children.values()
            _id = self.focused_sel
            spacer = ''
        else:
            return

        if not _id:
            name_label.configure(image=None, text='', bg='#232323')
            name_label.image = None

            points_label.configure(image=None, text='', bg='#232323')
            points_label.image = None

            req_label.configure(image=None, text='', bg='#232323')
            req_label.image = None

            time_label.configure(image=None, text='', bg='#232323')
            time_label.image = None
        else:
            _, name, points, req, time, *_, quest_img, quest_icon = db.get_quest_by_id(_id)

            img = load_quest_image(quest_img, resize=resize)
            bg = get_most_common_color(img)
            r, g, b = [int(x, 16) for x in (bg[1:3], bg[3:5], bg[5:])]

            while (r+g+b)//3 > 45:
                r *= .9
                g *= .9
                b *= .9
            bg = f'#{hex((int(r)*256*256 + int(g)*256 + int(b)))[2:]:0>6}'

            name_img = ImageTk.PhotoImage(img, 2)
            points_img = ImageTk.PhotoImage(load_icon_image(66, height=40, resize=resize))
            req_img = ImageTk.PhotoImage(load_icon_image(quest_icon, height=40, resize=resize))
            time_img = ImageTk.PhotoImage(load_icon_image(11, height=40, resize=resize))

            name_label.configure(image=name_img, text=name, bg=bg)
            name_label.image = name_img

            points_label.configure(image=points_img, text=f'{spacer}+{points}', bg=bg)
            points_label.image = points_img

            req_label.configure(image=req_img, text=f'{spacer}0 / {req}', bg=bg)
            req_label.image = req_img

            time_label.configure(image=time_img, text=f'{spacer}{time}', bg=bg)
            time_label.image = time_img

    @staticmethod
    def dragging(event, treeview):
        rowid = treeview.identify_row(event.y)
        treeview.selection_set(rowid)
        treeview.focus(rowid)

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
        sizes = ([1600, 13], [1500, 12], [1400, 11], [1300, 10], [1150, 9], [1050, 8], [1000, 7])
        buttons = self.tabs_frame.children.values()

        for w, size in sizes[::-1]:
            if w >= width:
                for button in buttons:
                    if button is self.last_button:
                        button.configure(font=(font, size, 'bold'))
                    else:
                        button.configure(font=(font, size, 'normal'))
                break
        else:
            for button in buttons:
                if button is self.last_button:
                    button.configure(font=(font, sizes[0][1], 'bold'))
                else:
                    button.configure(font=(font, sizes[0][1], 'normal'))

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
                    c.configure(font=('Gadugi', 10, 'bold'))
            if self.main_treeview.focus():
                self.refresh_details('main', .8)
        else:
            self.update_idletasks()
            for c in children:
                if self.main_treeview.focus():
                    c.configure(font=('Gadugi', 14, 'bold'))
            if self.main_treeview.focus():
                self.refresh_details('main', 1)

    def resize_details2(self):
        name, frame = self.details_frame2.children.values()
        name.configure(wraplength=name.winfo_width()-120-10)
        children = [name] + list(frame.children.values())

        if frame.winfo_height() < frame.winfo_reqheight():
            self.update_idletasks()
            for c in children:
                self.update_idletasks()
                c.configure(font=('Gadugi', 10, 'bold'))
            self.refresh_details('sel', .8)
        else:
            self.update_idletasks()
            for c in children:
                self.update_idletasks()
                c.configure(font=('Gadugi', 14, 'bold'))
            self.refresh_details('sel', 1)

    def call_start(self):
        from LMGF5 import main
        self.destroy()
        main()

    def call_pointers(self):
        import pointers_GUI
        pointers_GUI.ConfigGUI(self)


if __name__ == '__main__':
    gui = MainGUI().mainloop()
