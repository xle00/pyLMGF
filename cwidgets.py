import tkinter as tk
from tkinter import ttk

FONT = '-family Gadugi -weight bold '
YELLOW = '#f7e083'
MAIN_FG = '#efeee9'
REMOVE_RED = '#d3a9a9'
ADD_GREEN = '#bcd1c9'#'#87dbac'#'#87db87'
SELECTED_YELLOW = '#d1ae62'
BUTTON_BG = '#323536'
BUTTON_BG_HOVER = '#464646'
font = 'Segoe UI'
TV_BG = '#222222'


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


class Button(tk.Button):
    def __init__(self, parent, **kw):
        super(Button, self).__init__(parent)
        self.configure(
            bg=BUTTON_BG,
            fg=MAIN_FG,
            relief='flat',
            font=FONT + '-weight bold ',
            anchor='center',
            cursor='hand2',
        )
        self.config(**kw)
        self.config(
            activebackground=self.cget('fg'),
            activeforeground=self.cget('bg')
        )

        multiplier = 1.75
        bghex = self.cget('bg').replace('#', '')
        r, g, b = int(bghex[:2], 16)*multiplier, int(bghex[2:4], 16)*multiplier, int(bghex[4:], 16)*multiplier
        hover_rgb = f'#{bytearray([int(r), int(g), int(b)]).hex()}'

        bind_hover(self, bg=hover_rgb)


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
                       font=(font, 14),
                       rowheight=45,
                       background=TV_BG,
                       )

        # layout
        self.layout("treeview.Treeview", [
             ('treeview.Treeview.treearea', {'sticky': 'news'})])

        # map
        self.map('treeview.Treeview',
                 background=[('disabled', '#262626'), ('selected', ADD_GREEN)],
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
                            [("Custom2.Treeheading.image", {'side': 'right', 'sticky': ''}),
                                ("Custom2.Treeheading.text", {'sticky': 'we'})]})]}), ])

        # heading style
        self.configure("sectreeview.Treeview.Heading",
                       font=('Gadugi', 14, 'bold'),
                       background='#262626',
                       foreground='#d0d0d0'
                       )

        # heading map
        self.map("sectreeview.Treeview.Heading",
                 relief=[('active', 'flat'), ('pressed', 'sunken')],
                 # background=[('active', 'white')],
                 # foreground=[('active', 'black')])
                 )

        # style
        self.configure("sectreeview.Treeview",
                       highlightthickness=0,
                       bd=0,
                       font=('Gadugi', 10),
                       background='#222222',
                       rowheight=25
                       )

        # layout
        self.layout("sectreeview.Treeview", [
            ('sectreeview.Treeview.treearea', {'sticky': 'news'})])

        # map
        self.map('sectreeview.Treeview',
                 background=[('disabled', '#262626'), ('selected', REMOVE_RED)],
                 foreground=[('disabled', MAIN_FG), ('selected', '#262626')],
                 )


class Label(tk.Label):
    def __init__(self, parent, **kw):
        super(Label, self).__init__(parent)
        self.configure(
            bg='pink',
            fg=MAIN_FG,
            font=(font, 16, 'bold'),
        )
        self.config(**kw)