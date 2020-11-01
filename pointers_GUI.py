import tkinter as tk
from configs import Pointers

pointers = Pointers()

if __name__ == '__main__':
    top = tk.Tk
else:
    top = tk.Toplevel


class ConfigGUI(top):
    def __init__(self, parent=None):
        super(ConfigGUI, self).__init__(parent)
        from readprocessmemory import ProcessMemory
        self.pointers = pointers.get_pointers()
        self.lmp = ProcessMemory('Lords Mobile.exe')
        self.vars = {}

        self.create_pointers()
        self.test_pointers()

    def create_pointers(self):
        frame = tk.Frame(self, bg='#404040')
        frame.pack(fill='both', expand=1)

        for name, module, base_offset, *offsets in self.pointers:
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

            self.vars.update({name: [module_var, base_var, *offset_vars, result]})
            self.vars.update()

    def test_pointers(self):
        for name, _vars in self.vars.items():
            module = _vars[0].get()
            base_addr = int(_vars[1].get(), 16)
            offsets = [int(i.get(), 16) for i in _vars[2:-1]]
            result_label = _vars[-1]

            module_addr = self.lmp.get_module_address_by_name(module)
            addr = self.lmp.get_pointer(module_addr + base_addr, offsets)

            value = self.lmp.read_4_bytes(addr)
            string = self.lmp.read_string(addr, 50)

            if value:
                result_label.config(text=f'{value}\n{string}', fg='#22bb55')
            else:
                result_label.config(text='???', fg='#ff5555')

        self.after(1000, self.test_pointers)

    def update_pointers(self, name):
        _vars = self.vars[name]
        module = _vars[0].get()
        base_addr = _vars[1].get()
        offsets = ' '.join([i.get() for i in _vars[2:-1]])
        pointers.save_pointers(name, [module, base_addr, offsets])


if __name__ == '__main__':
    ConfigGUI().mainloop()
