import tkinter as tk
from lib.configs import *

if __name__ == '__main__':
    top = tk.Tk
else:
    top = tk.Toplevel


class ConfigGUI(top):
    def __init__(self, parent=None):
        self.offset_search_running = False
        self.current_offset = 0
        self.offset_search_id = None

        super(ConfigGUI, self).__init__(parent)
        from lib.Process import ProcessMemory
        self.pointers2 = Pointers.get_pointers_offline()

        self.lmp = ProcessMemory('Lords Mobile.exe')
        self.vars = {}

        self.create_pointers()
        self.test_pointers()
        self.create_controls()

    def create_controls(self):
        frame = tk.Frame(self)
        frame.pack(fill='both', expand=1)

        check_var = tk.IntVar(name='autosync', value=load_configs()['autosync'])
        checkbox = tk.Checkbutton(frame, text='Sincronizar ponteiros automaticamente', variable=check_var,
                                          bg='#262626', fg='#d0d0d0', selectcolor='#363636',
                                          cursor='hand2', activebackground='#d0d0d0', font=('Segoe UI', 14),
                                          activeforeground='#262626', command=self.toggle_autosync)
        checkbox.pack(fill='both', expand=1, side='left', )
        checkbox.variable = check_var

        button = tk.Button(frame, text='Sincronizar agora', command=self.sync_now, bg='#262626', fg='#d0d0d0',
                           font=('Segoe UI', 14))
        button.pack(fill='both', expand=1, side='left')

    @staticmethod
    def toggle_autosync():
        configs = load_configs()
        configs['autosync'] = not configs['autosync']
        save_configs(configs)

    def sync_now(self):
        pointers = Pointers.get_pointers()

        for key, values in pointers.items():
            module, base_offset, offsets = values

            module_var, base_var, *offset_vars, _ = self.vars[key]

            module_var.set(module)
            base_var.set(hex(base_offset)[2:].upper())
            for value, var in zip(offsets, offset_vars):
                var.set(hex(value)[2:].upper())

    def create_pointers(self):
        frame = tk.Frame(self, bg='#404040')
        frame.pack(fill='both', expand=1)

        for name, values in self.pointers2.items():
            module, base_offset, offsets = values

            f = tk.Frame(frame, bg='#404040')
            f.pack(fill='both', expand=1)

            label_frame = tk.LabelFrame(f, text=name, labelanchor='n', relief='flat', bg='#262626',
                                        fg='#97b6d8', font=('Gadugi', 15, 'bold'), pady=5)
            label_frame.pack(pady=4, fill='both', expand=1, side='left')

            module_var = tk.StringVar(self, module)
            module_var.trace_add('write', lambda *a, n=name: self.update_pointers(n))
            module_entry = tk.Entry(label_frame, textvariable=module_var, width=25, bg='#404040', relief='flat',
                                    fg='#d0d0d0', font=('Gadugi', 14))
            module_entry.pack(side='left', padx=4, expand=1)

            base_var = tk.StringVar(self, hex(base_offset)[2:].upper())
            base_var.trace_add('write', lambda *a, n=name: self.update_pointers(n))
            base_offset = tk.Entry(label_frame, textvariable=base_var, width=10, bg='#404040', relief='flat',
                                   fg='#d0d0d0', font=('Gadugi', 14))
            base_offset.pack(side='left', padx=4, expand=1)

            offset_vars = []
            for offset in offsets:
                offset_var = tk.StringVar(self, hex(offset)[2:].upper())
                offset_var.trace_add('write', lambda *a, n=name: self.update_pointers(n))
                offset_entry = tk.Entry(label_frame, textvariable=offset_var, width=5, bg='#404040', relief='flat',
                                        fg='#d0d0d0', font=('Gadugi', 14))
                offset_entry.pack(side='left', padx=4, expand=1)
                offset_vars.append(offset_var)

            result = tk.Label(f, width=40, bg='#262626', font=('Gadugi', 14, 'bold'))
            result.pack(side='right', pady=4, fill='both', expand=1,)

            button_frame = tk.Frame(f)
            button_frame.pack(side='right', fill='both')

            button = tk.Button(button_frame, bg='#262626', width=2, text="", fg='#d0d0d0',
                               command=lambda v=base_var, l=result, o=offset_vars, m=module_var:
                               self.find_new_base_wrapper(v, l, o, m),  font=('Segoe MDL2 Assets', 12, 'bold'),)
            button.pack(fill='both', expand=1)

            button2 = tk.Button(button_frame, bg='#262626', width=2, text='', fg='#d0d0d0',
                               command=lambda v=base_var, l=result, o=offset_vars, m=module_var:
                               self.find_new_base_wrapper(v, l, o, m, True), font=('Segoe MDL2 Assets', 12, 'bold'))
            button2.pack(fill='both', expand=1)

            self.vars.update({name: [module_var, base_var, *offset_vars, result]})

    def find_new_base_wrapper(self, var, label, offsets, module, down=False):
        if self.offset_search_running:
            self.after_cancel(self.offset_search_id)
            self.offset_search_running = False
        else:
            self.find_new_base(var, label, offsets, module, down)

    def find_new_base(self, var, label, offsets, module, down=False):
        self.offset_search_running = True
        max_offset = 50000
        curr = self.current_offset
        if abs(curr) == max_offset:
            return

        step = -1 if down else 1

        base_address = int(var.get(), 16)
        _module = self.lmp.get_module_address_by_name(module.get())
        _offsets = [int(var.get(), 16) for var in offsets]

        value = self.lmp.read_byte(self.lmp.get_pointer(_module + base_address + step, _offsets))

        if (curr == 0 and value) or not value:
            self.current_offset += step
            self.offset_search_id = self.after(1, self.find_new_base, var, label, offsets, module, down)
        else:
            self.offset_search_running = False

        var.set(hex(base_address+step)[2:])


    def test_pointers(self):
        for name, _vars in self.vars.items():
            module = _vars[0].get()

            try:
                base_addr = int(_vars[1].get(), 16)
            except ValueError:
                base_addr = 0

            offsets = [int(i.get(), 16) for i in _vars[2:-1] if i]

            result_label = _vars[-1]

            module_addr = self.lmp.get_module_address_by_name(module)
            addr = self.lmp.get_pointer(module_addr + base_addr, offsets)

            value = self.lmp.read_4_bytes(addr)
            string = self.lmp.read_string(addr, 50)

            if value:
                result_label.config(text=f'{value}\n{string}', fg='#22bb55')
            else:
                result_label.config(text='???', fg='#ff5555')

        self.after(100, self.test_pointers)

    def update_pointers(self, name):
        _vars = self.vars[name]
        module = _vars[0].get()
        base_addr = _vars[1].get()
        offsets = ' '.join([i.get() for i in _vars[2:-1]])

        Pointers.save_pointers(name, [module, base_addr, offsets])


if __name__ == '__main__':
    ConfigGUI().mainloop()
