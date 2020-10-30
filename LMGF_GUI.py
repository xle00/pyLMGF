# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from configs import QuestDB, Pointers

db = QuestDB()
pointers = Pointers()



'''class MainGUI:
    def __init__(self):
        self.active_button = None

        bg = '#242424'
        self.root = tk.Tk()
        self.root.geometry(root_geometry)
        self.root.configure(bg='#ffffff', borderwidth=0, relief='flat',
                            highlightbackground='black', highlightcolor='black')
        self.root.resizable(0, 0)
        self.root.title('pylmgf')

        self.rootframe = tk.Frame(self.root, bg='#ffd00a')

        self.scrollbar = None

        self.main_listbox = self.create_tabs2()
        self.rootframe.pack(fill='both', expand=1)

        p_frame = tk.Frame(self.rootframe, bg='#303030')
        p_frame.place(relx=0, y=p_frame_placement, relheight=1, relwidth=1)
        self.root.update_idletasks()
        half = self.root.winfo_width()*.75 / 2
        p_frame.columnconfigure(0, minsize=half)
        p_frame.columnconfigure(1, minsize=half)

        add_button = tk.Button(p_frame, text='Adicionar às Missões Selecionadas', command=self.add_to_selected,
                               font='-family {Courier} -size 14', bg='#262626', fg='#ffffff',
                               activebackground='#a3e3a3', relief='flat', )
        add_button.grid(row=0, column=0, columnspan=2, sticky='we', padx=5, pady=5)

        selected_frame = tk.Frame(p_frame, bg='#303030')
        selected_frame.grid(row=1, column=0, sticky='we', padx=5, pady=5)

        selected_frame.grid_columnconfigure(0, minsize=420)

        sel_lb_label = tk.Label(selected_frame, text='Missões Selecionadas')
        sel_lb_label.configure(bg='#262626', fg='#ffffff', font='-family {Courier new} -size 12', relief='flat')
        sel_lb_label.grid(row=0, column=0, columnspan=2, sticky='nsew')

        selected_scrollbar = tk.Scrollbar(selected_frame)
        selected_scrollbar.grid(row=1, column=1, sticky='nsew')

        self.selected_lb = tk.Listbox(selected_frame, yscrollcommand=selected_scrollbar.set)
        self.selected_lb.grid(row=1, column=0, sticky='nsew')
        self.selected_lb.configure(activestyle='none', justify='center', relief='flat', selectmode='extended',
                                   font='-family {Courier new} -size 10', bg='#242424', fg='#ffffff',
                                   selectbackground='#a3e3e3', selectforeground='#020202',
                                   highlightcolor='#242424', highlightbackground='#242424')

        selected_scrollbar.config(command=self.selected_lb.yview)

        remove_button = tk.Button(selected_frame, text='Remover Missões', command=self.remove_item)
        remove_button.configure(bg='#202020', fg='#ffffff', activebackground='#df5454',
                                relief='flat', font='-family {Courier new} -size 10')
        remove_button.grid(row=2, column=0, columnspan=2, sticky='nsew')

        buttons_frame = tk.Frame(p_frame, bg='#303030')
        buttons_frame.grid(row=1, column=1, sticky='we', padx=5, pady=5)

        self.pointers_button = tk.Button(buttons_frame, text='Ponteiros', bg='#202020', fg='#ffffff', relief='flat',
                                         font='-family {Arial} -size 24 -weight bold',
                                         command=self.config_launcher)
        self.pointers_button.pack(fill='both', padx=5, pady=5)

        self.history_button = tk.Button(buttons_frame, text='Histórico', bg='#202020', fg='#ffffff', relief='flat',
                                        font='-family {Arial} -size 24 -weight bold',
                                        command=self.history_launcher)
        self.history_button.pack(fill='both', padx=5, pady=5)

        self.start_button = tk.Button(buttons_frame, text='Começar', command=self._start)
        self.start_button.configure(bg='#202020', fg='#ffffff', activebackground='#a3e3e3',
                                    relief='flat', font='-family {Arial} -size 24 -weight bold')
        self.start_button.pack(fill='both', padx=5, pady=5)

        self.selected_quests_ids = []

        if selected_quests:
            self.insert_selected()

        self.details_frame = tk.Frame(self.rootframe)
        self.details_frame.place(relx=.75, rely=0, relwidth=1, relheight=1)

        self.details1 = self.create_detail(bg, 0, 0, 1, p_frame_placement)
        self.details2 = self.create_detail(bg, 0, p_frame_placement, 1, 1)

        self.updater()
        self.updater2()

        self.root.mainloop()

    def create_detail(self, bg, x, y, width, height, ):
        frame = tk.Frame(self.details_frame, bg=bg, relief='flat')
        frame.place(y=y-7, relx=x, relwidth=width, relheight=height, )

        img = tk.PhotoImage(master=frame, file='imgs\\031.png')
        img_label = tk.Label(frame, bg='#242424', image=img, borderwidth=0)
        img_label.grid(row=0, column=0, sticky='nsew', pady=8, ipady=2, ipadx=2)

        points_label = tk.Label(frame, text='', bg=bg, fg='#f0f0ff', width=9,
                                font='-family {Gadugi} -size 24 -weight bold', justify='left')
        points_label.grid(column=1, row=0, sticky='nsew', pady=10, )

        name_label = tk.Label(frame, text='', bg=bg, fg='#F9EE54',
                              font='-family {Courier New} -size 12 -weight bold', justify='center')
        name_label.grid(column=0, row=1, sticky='nsew', pady=5, columnspan=2)

        req_label = tk.Label(frame, text='', bg=bg, fg='#f0f0ff',
                             font='-family {Gadugi} -size 24 -weight bold', justify='center')
        req_label.grid(column=0, row=2, sticky='nsew', pady=2, columnspan=2)

        q_time_label = tk.Label(frame, text='', bg=bg, fg='#f0f0ff',
                                font='-family {Gadugi} -size 24 -weight bold', justify='center')
        q_time_label.grid(column=0, row=3, sticky='nsew', pady=2, columnspan=2)

        return {'img': img, 'img_label': img_label, 'points': points_label, 'name': name_label,
                'req': req_label, 'time': q_time_label}

    def updater(self):
        items = self.get_selected_items()

        if items:
            _id = items[len(items)-1][1]
            if _id == -1:
                self.root.after(100, self.updater)
                return

            _, name, points, req, time, *_, image = db.get_quest_by_id(_id)

            if image:
                self.details1['img'].configure(file=f'imgs\\{image:03d}.png')
            else:
                self.details1['img'].configure(file=f'imgs\\{0:03d}.png')

            wrapper_length = 29
            if len(name) > wrapper_length:
                _name = name[:wrapper_length]
                _name = _name[::-1]
                _index = _name.find(' ')
                name = name[:wrapper_length - _index - 1] + '\n' + name[wrapper_length - _index:]
            else:
                name += '\n'

            if _id in self.selected_quests_ids:
                self.details1['img_label'].configure(bg='#F9EE54')
            else:
                self.details1['img_label'].configure(bg='#242424')

            self.details1['name'].config(text=name)
            self.details1['points'].config(text='+' + str(points))
            self.details1['req'].config(text='0 / ' + req)
            self.details1['time'].config(text=time)
        else:
            self.details1['img'].configure(file=f'imgs\\{0:03d}.png')
            self.details1['img_label'].configure(bg='#242424')
            self.details1['name'].config(text='\n')
            self.details1['points'].config(text='')
            self.details1['req'].config(text='')
            self.details1['time'].config(text='')

        self.up1 = self.root.after(100, self.updater)

    def updater2(self):
        indexes = self.selected_lb.curselection()
        if indexes:
            index = indexes[::-1][0]

            _id = self.selected_quests_ids[index]
            _, name, points, req, time, *_, image = db.get_quest_by_id(_id)

            if image:
                self.details2['img'].configure(file=f'imgs\\{image:03d}.png')
            else:
                self.details2['img'].configure(file=f'imgs\\{0:03d}.png')

            wrapper_length = 29
            if len(name) > wrapper_length:
                _name = name[:wrapper_length]
                _name = _name[::-1]
                _index = _name.find(' ')
                name = name[:wrapper_length - _index - 1] + '\n' + name[wrapper_length - _index:]
            else:
                name += '\n'

            self.details2['name'].config(text=name)
            self.details2['points'].config(text='+' + str(points))
            self.details2['req'].config(text='0 / ' + req)
            self.details2['time'].config(text=time)

        else:
            self.details2['img'].configure(file=f'imgs\\{0:03d}.png')
            self.details2['img_label'].grid_configure(ipadx=0, ipady=0)
            self.details2['name'].config(text='\n')
            self.details2['points'].config(text='')
            self.details2['req'].config(text='')
            self.details2['time'].config(text='')

        self.up2 = self.root.after(100, self.updater2)

'''


def invert_on_hover(widget: tk.Widget):
    fg = widget.cget('fg')
    bg = widget.cget('bg')

    widget.bind('<Enter>', lambda e: widget.configure(fg=bg, bg=fg))
    widget.bind('<Leave>', lambda e: widget.configure(fg=fg, bg=bg))


def unbind_invert(widget: tk.Widget):
    widget.bind('<Enter>', lambda e: None)
    widget.bind('<Leave>', lambda e: None)


def load_quest_image(img_index):
    path = f'imgs\\quests\\{int(img_index):03d}.png'
    img = Image.open(path)
    return img


def load_icon_image(img_index):
    img_index = 35 if not img_index else img_index
    path = f'imgs\\icons\\{int(img_index):03d}.png'
    img = Image.open(path)
    return img


class Button(tk.Button):
    def __init__(self, parent, **kw):
        super(Button, self).__init__(parent, **kw)
        self.configure(
            bg='#262626',
            fg='#ffffff',
            relief='flat',
            font='-size 9',
            anchor='center',
            cursor='hand2',
        )
        invert_on_hover(self)


class TreeView(ttk.Treeview):
    def __init__(self, parent, **kw):
        super(TreeView, self).__init__(parent, **kw)
        self.configure(
            selectmode='extended'
        )
        print(self.keys())


class Label(tk.Label):
    def __init__(self, parent, **kw):
        super(Label, self).__init__(parent, **kw)
        self.configure(
            bg='pink',
            fg='black',
        )


class MainGUI(tk.Tk):
    def __init__(self):
        super(MainGUI, self).__init__()
        self.geometry('1210x670')

        self.last_button = None

        self.main_treeview = TreeView(None)
        self.focused_item = None

        self.sel_treeview = TreeView(None)

        self.name_var1 = tk.StringVar()
        self.points_var1 = tk.StringVar()
        self.req_var1 = tk.StringVar()
        self.time_var1 = tk.StringVar()

        self.tabs_frame = tk.Frame(bg='red')
        self.tabs_frame.place(x=0, y=0, relwidth=1, height=26)

        self.treeview_frame = tk.Frame(bg='yellow')
        self.treeview_frame.place(x=0, y=26, width=900, height=410)

        self.selected_quests_frame = tk.Frame(bg='blue')
        self.selected_quests_frame.place(x=0, y=410+26, height=670-410-26, width=450)

        self.buttons_frame = tk.Frame(bg='orange')
        self.buttons_frame.place(x=900, y=410+26, height=670-410-26, width=1210-900)

        self.details_frame1 = tk.Frame(bg='cyan')
        self.details_frame1.place(x=900, y=26, width=1210-900, height=410)

        self.details_frame2 = tk.Frame(bg='purple')
        self.details_frame2.place(x=450, y=410+26, height=670-410-26, width=450)

        self.populate_tab_frame()
        self.populate_treeview_frame()
        self.populate_selected_frame()
        self.populate_buttons_frame()
        self.populate_details_frame1()
        self.populate_details_frame2()
        self.change_listener()

    def populate_tab_frame(self):
        for tab in db.get_categories():
            button = Button(self.tabs_frame, text=tab)
            button['command'] = lambda t=tab, b=button: self.tab_button_command(t, b)
            button.pack(side='left')

    def populate_treeview_frame(self):
        scrollbar = tk.Scrollbar(self.treeview_frame, orient='vertical')
        scrollbar.pack(side='right', fill='y')

        treeview = self.main_treeview = TreeView(self.treeview_frame, displaycolumns='#all', yscrollcommand=scrollbar.set)
        self.main_treeview['columns'] = (
            'Name', 'Points', 'Requirements'
        )
        self.main_treeview.pack(fill='both', expand=1)

        scrollbar['command'] = self.main_treeview.yview

        button = Button(self.treeview_frame, text='Adicionar Missão', command=self.add_to_selected)
        button.pack(fill='both')

        treeview.heading('#0', anchor='n', text='')
        treeview.heading('Name', anchor='n', text='Missão')
        treeview.heading('Points', anchor='n', text='Pontos')
        treeview.heading('Requirements', anchor='n', text='Meta')

        treeview.column('#0', minwidth=40, width=40, stretch=0, anchor='n')
        treeview.column('Name', minwidth=700, width=700, stretch=0, anchor='n')
        treeview.column('Points', minwidth=60, width=60, stretch=0, anchor='n')
        treeview.column('Requirements', minwidth=80, width=80, stretch=0, anchor='n')

    def populate_selected_frame(self):
        # label = tk.Label(self.selected_quests_frame, textvariable=self.sel_label_var)
        # label.pack(fill='both')

        button = Button(self.selected_quests_frame, text='Remover Missão', command=self.remove_from_selected)
        button.pack(fill='both')

        treeview = self.sel_treeview = TreeView(self.selected_quests_frame)
        treeview.configure(columns=('Name', 'Points'))
        treeview.pack(fill='both', expand=1)

        treeview.heading('#0', anchor='n', text='')
        treeview.heading('Name', anchor='n', text='Missão')
        treeview.heading('Points', anchor='n', text='Pontos')

        treeview.column('#0', minwidth=40, width=40, stretch=0, anchor='n')
        treeview.column('Name', minwidth=35, width=350, stretch=0, anchor='n')
        treeview.column('Points', minwidth=58, width=58, stretch=0, anchor='n')

    def populate_buttons_frame(self):
        buttons = [['Começar', 'call_start'], ['Configurações', 'call_config'], ['Histórico', 'call_history']]
        for text, command in buttons:
            button = Button(self.buttons_frame, text=text, command=getattr(self, command, None))
            button.pack(fill='both', expand=1)

    def populate_details_frame1(self):
        name_label = Label(self.details_frame1, compound='top')#, textvariable=self.name_var1)
        name_label.pack()

        points_label = Label(self.details_frame1, compound='left')#, textvariable=self.points_var1)
        points_label.pack()

        req_label = Label(self.details_frame1, compound='left')#, textvariable=self.req_var1)
        req_label.pack()

        time_label = Label(self.details_frame1, compound='left')#, textvariable=self.time_var1)
        time_label.pack()

    def populate_details_frame2(self):
        pass

    def add_to_selected(self):
        selected = self.get_selected_from_main()

        for quest in selected:
            iid = quest['Id']
            name = quest['Name']
            points = quest['Points']
            self.sel_treeview.insert('', 'end', iid=iid, values=(name, points))

    def remove_from_selected(self):
        selected = self.sel_treeview.selection()
        self.sel_treeview.delete(*selected)

    def tab_button_command(self, tab, button):
        unbind_invert(button)
        if self.last_button:
            self.last_button.configure(bg='#262626', fg='#ffffff',)
            invert_on_hover(self.last_button)
        button.configure(bg='red', fg='cyan')
        self.last_button = button

        self.populate_main_treeview(tab)

    def populate_main_treeview(self, category):
        self.main_treeview.delete(*self.main_treeview.get_children())
        quests = db.get_quests_by_category(category)
        for quest_id, name, points, req, *_, img in quests:
            self.main_treeview.insert('', 'end', iid=quest_id, values=(name, points, req))

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
            self.refresh_details1(q_id)
        self.focused_item = q_id

        self.after(100, self.change_listener)

    def refresh_details1(self, _id):
        name_label, points_label, req_label, time_label = self.details_frame1.children.values()

        if not _id:
            name_label.configure(image=None, text='')
            name_label.image = None

            points_label.configure(image=None, text='')
            points_label.image = None

            req_label.configure(image=None, text='')
            req_label.image = None

            time_label.configure(image=None, text='')
            time_label.image = None
        else:
            _, name, points, req, time, *_, quest_img, quest_icon = db.get_quest_by_id(_id)

            name_img = ImageTk.PhotoImage(load_quest_image(quest_img))
            points_img = ImageTk.PhotoImage(load_icon_image(66))
            req_img = ImageTk.PhotoImage(load_icon_image(quest_icon))
            time_img = ImageTk.PhotoImage(load_icon_image(11))

            name_label.configure(image=name_img, text=name)
            name_label.image = name_img

            points_label.configure(image=points_img, text=points)
            points_label.image = points_img

            req_label.configure(image=req_img, text=req)
            req_label.image = req_img

            time_label.configure(image=time_img, text=time)
            time_label.image = time_img

        # self.name_var1.set(name)
        # self.points_var1.set(points)
        # self.req_var1.set(req)
        # self.time_var1.set(time)







class ConfigGUI:
    def __init__(self):
        from readprocessmemory import ProcessMemory
        self.lmp = ProcessMemory('Lords Mobile.exe')

        self.root = tk.Tk()
        self.root.resizable(0, 0)
        self.root.configure(bg='#303030', borderwidth=0, relief='flat',
                            highlightbackground='black', highlightcolor='black')
        self.root.title('pylmgf - Ponteiros')

        self.time = self.create_inputs('Tempo', 0, 0)
        self.quest_p = self.create_inputs('Pontos da Missão', 0, 1)
        self.quest_r = self.create_inputs('Meta da Missão', 0, 2)
        self.quest_t = self.create_inputs('Tempo da Missão',  1, 0)
        self.name = self.create_inputs('Nome', 1, 1)
        self.clock = self.create_inputs('Relógio', 1, 2)
        self.populate_inputs(self.time, 'active_time')
        self.populate_inputs(self.quest_p, 'quest_points')
        self.populate_inputs(self.quest_r, 'quest_requirements')
        self.populate_inputs(self.quest_t, 'quest_time')
        self.populate_inputs(self.name, 'player_name')
        self.populate_inputs(self.clock, 'clock')

        save_button = tk.Button(self.root, text='Salvar', width=40, height=1, bg='#202020',
                                font='-family {Segoe UI} -size 10 -weight bold', relief='flat', fg='#fdfdfd',
                                command=self.save_pointers)
        save_button.grid(column=1, ipady=_pad, pady=_pad)
        self.test_pointers(self.time, 'string')
        self.test_pointers(self.quest_p, 'string')
        self.test_pointers(self.quest_r, 'string')
        self.test_pointers(self.quest_t, 'string')
        self.test_pointers(self.name, 'string')
        self.test_pointers(self.clock, '4bytes')


        self.root.mainloop()

    def create_inputs(self, label, row, column):
        label_frame = tk.LabelFrame(self.root, relief='flat', labelanchor="n",
                                    text=label, highlightbackground="#f0f0f0f0f0f0", bg='#404040', fg='#2288fe',
                                    font=f'-family {{Segoe UI}} -size {c_font1_size} -weight bold')

        label_frame.grid_columnconfigure(0, minsize=80)
        label_frame.grid_columnconfigure(1, minsize=80)

        module_input = tk.Entry(label_frame, width=20, relief='solid', justify=tk.CENTER, bg='#505050', fg='#ffffff',
                                font=f'-family {{Segoe UI}} -size {c_font2_size}', insertbackground='#ffffff')
        module_input.grid(row=0, column=1, padx=5)
        module_label = tk.Label(label_frame, justify='left', text='Module: ', bg='#404040', fg='#e1e2e1')
        module_label.grid(row=0, column=0, padx=5, sticky='w', pady=3)

        base_input = tk.Entry(label_frame, width=20, relief='solid', justify=tk.CENTER, bg='#505050', fg='#ffffff',
                              font=f'-family {{Segoe UI}} -size {c_font2_size}', insertbackground='#ffffff')
        base_input.grid(row=1, column=1, padx=5)
        base_label = tk.Label(label_frame, justify='left', text='Base Pointer: ', bg='#404040', fg='#e1e2e1')
        base_label.grid(row=1, column=0, padx=5, sticky='w', pady=3)

        for i in range(2, 9):
            pointer_label = tk.Label(label_frame, justify='left', text=f'Pointer {i}: ', anchor='w', bg='#404040',
                                     fg='#e1e2e1')
            pointer_label.grid(row=i, column=0, sticky='w', padx=5)

            p_input = tk.Entry(label_frame, width=20, relief='solid', justify=tk.CENTER, bg='#505050', fg='#ffffff',
                               font=f'-family {{Segoe UI}} -size {c_font2_size}', insertbackground='#ffffff')
            p_input.grid(row=i, column=1, pady=3, padx=5)

        label_frame.grid(row=row, column=column, padx=10, pady=10, ipadx=10)

        button = tk.Button(label_frame, width=10, font='-family {Segoe UI} -size 10')
        button.configure(text='Testar', bg='#202020', relief='flat', fg='#fdfdfd',
                         command=lambda lf_object=label_frame: self.test_pointers(lf_object))
        button.grid(row=9, pady=3, ipadx=10, padx=5)

        output = tk.Entry(label_frame, width=20, relief='flat', bg='#404040', fg='#ffffff', justify='center',
                          font=f'-family {{Segoe UI}} -size {c_font1_size} -weight bold')
        output.grid(row=9, column=1, pady=3, padx=5)

        return label_frame

    @staticmethod
    def populate_inputs(inputs, populator):
        module, base_address, pointers_ = pointers.get_pointers(populator)
        values = [module, base_address] + pointers_
        # print(values)
        index = 0
        for children_name, children in inputs.children.items():
            if type(children) is tk.Entry and children_name != '!entry10':
                if isinstance(values[index], int):
                    children.insert(0, str(hex(values[index]))[2::].upper())
                else:
                    children.insert(0, values[index])
                index += 1

    def test_pointers(self, label_frame, _type=None):
        output_entry = label_frame.children['!entry10']
        # print(label_frame.children.items())
        try:
            values = [int(child.get(), 16) for child_name, child in label_frame.children.items()
                      if type(child) is tk.Entry and child_name != '!entry10' and child_name != '!entry']
            _, module = list(label_frame.children.items())[0]
            module = module.get()
            # values.insert(0, module)
        except ValueError as e:
            print('Value Error', e)
            return
        # print(values)

        base_address = self.lmp.get_module_address_by_name(module)
        address = self.lmp.get_pointer(base_address + values[0], values[1::])
        if _type == 'string':
            result = self.lmp.read_string(address, 40)
        else:
            result = self.lmp.read_8_bytes(address)

        # result = result if result else "???????"

        output_entry.delete(0, tk.END)
        if result:
            output_entry.configure(fg='#22bb55')
            output_entry.insert(0, result)
        else:
            output_entry.configure(fg='#ff5555')
            output_entry.insert(0, '?????????')

        self.root.after(100, self.test_pointers, label_frame, _type)

    def save_pointers(self):
        names = ['active_time', 'quest_points', 'quest_requirements', 'quest_time', 'player_name', 'clock']
        label_frames = [lf for lf in self.root.children.values() if isinstance(lf, tk.LabelFrame)]

        for item, name in zip(label_frames, names):
            values = [child.get() for child_name, child in item.children.items() if
                      type(child) is tk.Entry and child_name != '!entry10']
            # print(values)
            pointers.save_pointers(values, name)

        self.root.destroy()


class HistoryGUI:
    def __init__(self):
        bg = '#202c3c'
        self.root = tk.Tk()
        self.root.geometry('1200x560')
        self.root.columnconfigure(0, minsize=500)
        self.root.resizable(0, 0)
        self.root.title('pylmgf - Histórico')

        lb_frame = tk.Frame(self.root, bg='#aa0000')
        lb_frame.place(relx=0, relwidth=.75, rely=0, relheight=1)

        self.listbox = tk.Listbox(lb_frame, height=25)
        self.listbox.pack(fill='both')
        self.listbox.configure(bg='#1B1F24', fg='#f0f0ff', activestyle='none', justify='left', relief='flat',
                               font='-family {Courier New} -size 11',
                               selectbackground='#3F5776', selectforeground='#f0f0ff', borderwidth=5,
                               highlightcolor='black', highlightbackground='black',
                               selectborderwidth=2, highlightthickness=0)
        self.current_page = 0

        self.populate_listbox()

        detail_frame = tk.Frame(self.root, bg=bg)
        detail_frame.place(relx=.75, relwidth=1, rely=0, relheight=1)

        detail_frame.grid_columnconfigure(0, minsize=299)

        self.account_label = tk.Label(detail_frame, text='', bg=bg, fg='#bcbcbc',
                                      font='-family {Gadugi} -size 20 -weight bold', justify='center')
        self.account_label.grid(columnspan=3, column=0, row=0, sticky='nsew')

        self.date_label = tk.Label(detail_frame, text='', bg=bg, fg='#f0f0ff',
                                   font='-family {Gadugi} -size 20 -weight bold', justify='center')
        self.date_label.grid(columnspan=3, column=0, row=1, sticky='nsew')

        self.time_label = tk.Label(detail_frame, text='', bg=bg, fg='#f0f0ff',
                                   font='-family {Gadugi} -size 20 -weight bold', justify='center')
        self.time_label.grid(columnspan=3, column=0, row=2, sticky='nsew')

        self.img = tk.PhotoImage(master=detail_frame, file='imgs\\00.png')
        self.img_label = tk.Label(detail_frame, image=self.img, pady=200, relief='groove',
                                  borderwidth=0)
        self.img_label.grid(columnspan=3, row=3, pady=10)

        self.name_label = tk.Label(detail_frame, text='\n', bg=bg, fg='#F9EE54',
                                   font='-family {Courier New} -size 12 -weight bold', justify='center')
        self.name_label.grid(columnspan=3, column=0, row=4, sticky='nsew', pady=10)

        self.points_label = tk.Label(detail_frame, text='', bg=bg, fg='#f0f0ff',
                                     font='-family {Gadugi} -size 24 -weight bold', justify='center')
        self.points_label.grid(columnspan=3, column=0, row=5, sticky='nsew', pady=10)

        self.req_label = tk.Label(detail_frame, text='', bg=bg, fg='#f0f0ff',
                                  font='-family {Gadugi} -size 24 -weight bold', justify='center')
        self.req_label.grid(columnspan=3, column=0, row=6, sticky='nsew', pady=10)

        self.q_time_label = tk.Label(detail_frame, text='', bg=bg, fg='#f0f0ff',
                                     font='-family {Gadugi} -size 24 -weight bold', justify='center')
        self.q_time_label.grid(columnspan=3, column=0, row=7, sticky='nsew', pady=10)

        self.refresh_button = tk.Button(detail_frame, text='Atualizar', command=self.refresh,
                                        font='-family {Gadugi} -size 20 -weight bold',)
        self.refresh_button.grid(column=0, row=8, sticky='sew')

        self.root.after(100, self.updater)

        self.root.mainloop()

    def refresh(self):
        self.listbox.delete(0, tk.END)
        self.populate_listbox()

    def updater(self):
        counter = 1
        index = self.listbox.curselection()
        if index:
            self.account_label.config(bg='#0C1015')
            self.date_label.config(bg='#161D26')
            self.time_label.config(bg='#161D26')
            try:
                n, date, hour, *_, acc, _id, grabbed = self.listbox.get(index).split()
                _, name, points, req, time, *_, image = db.get_quest_by_id(_id)
            except ValueError:
                date, hour, acc, name, points, req, time, image, grabbed = '', '', '', '', '', '', '', 0, None
            if image:
                self.img.configure(file=f'imgs\\{image:03d}.png')
            else:
                self.img.configure(file=f'imgs\\{0:03d}.png')

            if grabbed == '1':
                self.account_label.config(fg='#65E984')
            else:
                self.account_label.config(fg='#bcbcbc')

            wrapper_length = 29
            if len(name) > wrapper_length:
                _name = name[:wrapper_length]
                _name = _name[::-1]
                _index = _name.find(' ')
                name = name[:wrapper_length-_index-1] + '\n' + name[wrapper_length-_index:]
            else:
                name += '\n'

            self.account_label.config(text=acc)
            self.date_label.config(text=date)
            self.time_label.config(text=hour)
            self.name_label.config(text=name)
            self.points_label.config(text='+'+str(points))
            self.req_label.config(text='0 / '+req)
            self.q_time_label.config(text=time)
        counter += 1
        self.root.after(100, self.updater)

    def populate_listbox(self):
        try:
            with open('history.txt', 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            return

        for n, line in enumerate(lines):

            try:
                year, month, day, hour, minute, second, quest_id, grabbed, account = line.split()
            except ValueError:
                continue

            if quest_id == -1:
                continue

            limiter = 54
            try:
                #print(quest_id)
                _, name, points, requirement, time, *_ = db.get_quest_by_id(quest_id)

            except TypeError:
                continue

            if len(name) > limiter:
                name = name[:limiter-2]+'..'

            text = f'{n:<5}  {day}/{month}/{year} {hour}:{minute}:{second}   {name:<{limiter}}   {account:<12}' \
                   f'   {quest_id} {grabbed}'

            self.listbox.insert(tk.END, text)


if __name__ == '__main__':
    gui = MainGUI().mainloop()
