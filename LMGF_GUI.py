# -*- coding: utf-8 -*-
import tkinter as tk
import ctypes
import threading
from tkinter import ttk

from configs import QuestDB, Pointers

db = QuestDB()
quests = db.quest_db
selected_quests = db.selected
'''tab_names = ['Caixa Misteriosa', 'Monstro', 'Eventos', 'Poder', 'Heróis', 'Coleta', 'Missões', 'Pacotes',
             'Labirinto', 'Ninho', 'Familiar', 'Magnatas', 'Pesquisa', 'Aleatórias', 'Suprimento',
             'Cargueiro', 'Outras']'''
tab_names = set((quest[6] for quest in quests))
tab_names = sorted([tab_name for tab_name in tab_names if tab_name is not None])
pointers = Pointers()

screen_height = ctypes.windll.user32.GetSystemMetrics(1)
if screen_height < 800:
    detail_rely = .032
    list_box_height = 12
    p_frame_placement = 321
    detail_placement = p_frame_placement - detail_rely
    root_geometry = '1210x635'

    c_font1_size = 12
    c_font2_size = 9
    _pad = 1
else:
    detail_rely = .027
    list_box_height = 17
    p_frame_placement = 451
    detail_placement = p_frame_placement - detail_rely
    root_geometry = '1210x760+50+50'

    c_font1_size = 15
    c_font2_size = 12
    _pad = 10


class MainGUI:
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

        img = tk.PhotoImage(master=frame, file='Imgs\\031.png')
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
                self.details1['img'].configure(file=f'Imgs\\{image:03d}.png')
            else:
                self.details1['img'].configure(file=f'Imgs\\{0:03d}.png')

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
            self.details1['img'].configure(file=f'Imgs\\{0:03d}.png')
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
                self.details2['img'].configure(file=f'Imgs\\{image:03d}.png')
            else:
                self.details2['img'].configure(file=f'Imgs\\{0:03d}.png')

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
            self.details2['img'].configure(file=f'Imgs\\{0:03d}.png')
            self.details2['img_label'].grid_configure(ipadx=0, ipady=0)
            self.details2['name'].config(text='\n')
            self.details2['points'].config(text='')
            self.details2['req'].config(text='')
            self.details2['time'].config(text='')

        self.up2 = self.root.after(100, self.updater2)

    def insert_selected(self):
        for quest in selected_quests:
            text = str(f'{quest[1]}, +{quest[2]}')
            self.selected_lb.insert('end', text)
            self.selected_quests_ids.append(int(quest[0]))

    def create_tabs2(self):
        tabs_frame = tk.Frame(self.root, bg='#262626')
        tabs_frame.pack(fill='x')
        separator = tk.Frame(self.root, bg='#ffffff', height='2')
        separator.pack(fill='x')

        for n, tab in enumerate(tab_names):
            button = tk.Button(tabs_frame, text=tab, bg='#262626', fg='#ffffff', relief='flat', padx=2,
                               font='-size 9', anchor='center')
            button['command'] = lambda arg1=tab, arg2=button: self.refresh_tabs(arg1, arg2)

            button.grid(row=0, column=n)

        lb_frame = tk.Frame(self.rootframe, bg='green')
        lb_frame.place(relx=0, rely=0, relwidth=.75, relheight=p_frame_placement,)
        lb_frame.columnconfigure(0, minsize=890)
        lb_frame.columnconfigure(1, minsize=18)

        self.scrollbar = ttk.Scrollbar(lb_frame, style='Vertical.TScrollbar')
        self.scrollbar.grid(row=0, column=1, sticky='nsew')

        listbox = tk.Listbox(lb_frame, bg='#242424', fg='#ffffff', activestyle='none', justify='left',
                             relief='flat', selectmode='extended', font='-family {Courier New} -size 14',
                             height=list_box_height, selectbackground='#a3e3a3', selectforeground='#020202',
                             borderwidth=5, highlightcolor='black', highlightbackground='black', selectborderwidth=2,
                             highlightthickness=0, yscrollcommand=self.scrollbar.set)

        listbox.grid(row=0, column=0, sticky='nsew')
        self.scrollbar.config(command=listbox.yview)

        return listbox

    def refresh_tabs(self, tab_name, button):
        if button == self.active_button:
            return

        if isinstance(button, tk.Button):
            button.config(bg='#ffffff', fg='black', font='-size 9 -weight bold', relief='flat')
            if isinstance(self.active_button, tk.Button):
                self.active_button.config(bg='#262626', fg='white', font='-size 9', relief='flat')

        self.main_listbox.delete(0, 'end')
        # print(tab_name)
        result = db.cursor.execute('SELECT * from quests where tab_name = ?', (tab_name,)).fetchall()
        names = list(set([item[1] for item in result]))
        names.sort()
        for name in names:
            for quest in quests:
                if quest[6] == tab_name and quest[1] == name:
                    string = f'{quest[0]:<3}| {quest[1]:^67} | +{quest[2]:^3} |'
                    self.main_listbox.insert(tk.END, string)
        self.active_button = button

    def get_selected_items(self):
        indexes = self.main_listbox.curselection()
        if indexes:
            items = self.main_listbox.get(indexes[0], indexes[::-1][0])
            result = []
            for item in items:
                text_list = item.split('|')
                text_list = [str(string).strip() for string in text_list]
                _id = int(text_list[0]) if text_list[0] else -1
                result.append([f'{text_list[1]}, {text_list[2]}', _id])

            return result
        return []

    def add_to_selected(self):
        items = self.get_selected_items()
        for text, q_id in items:
            if q_id in self.selected_quests_ids:
                continue
            else:
                self.selected_quests_ids.append(q_id)
                self.selected_lb.insert('end', text)
        print(self.selected_quests_ids)

    def remove_item(self):
        try:
            index = self.selected_lb.curselection()
            for i in list(index)[::-1]:

                print('Removeu [Id: ' + str(self.selected_quests_ids[i]), self.selected_lb.get(i) + ']')
                self.selected_lb.delete(i)
                self.selected_quests_ids.pop(i)
        except IndexError:
            return

    def _start(self):
        db.update_selected(self.selected_quests_ids)
        from LMGF4 import main
        self.root.after_cancel(self.up1)
        self.root.after_cancel(self.up2)
        self.root.destroy()
        main()

    def config_launcher(self):
        thread = threading.Thread(target=self.config_gui)
        thread.start()

    def config_gui(self):
        self.pointers_button.config(state='disabled')
        ConfigGUI()
        self.pointers_button.config(state='normal')

    def history_launcher(self):
        thread = threading.Thread(target=self.history_gui, daemon=True)
        thread.start()

    def history_gui(self):
        self.history_button.config(state='disabled')
        HistoryGUI()
        self.history_button.config(state='normal')


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

        self.img = tk.PhotoImage(master=detail_frame, file='Imgs\\00.png')
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
                self.img.configure(file=f'Imgs\\{image:03d}.png')
            else:
                self.img.configure(file=f'Imgs\\{0:03d}.png')

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
    gui = MainGUI()
