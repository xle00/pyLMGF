import tkinter as tk
from tkinter import ttk


YELLOW = '#f7e083'
# MAIN_FG = '#efeee9'
MAIN_FG = '#e7e2d6'
ALT_FG = '#dfdace'
REMOVE_RED = '#d3a9a9'
ADD_GREEN = '#bcd1c9'#'#87dbac'#'#87db87'
SELECTED_YELLOW = '#d1ae62'
BUTTON_BG = '#323536'
BUTTON_BG_HOVER = '#464646'
FONT = 'Segoe UI'
TV_BG = '#222222'
HEADING_BG = '#363636'
DARK_BLUE = "#123541"


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
            font=(FONT, 10, 'bold'),
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


class CustomStyle(ttk.Style):
    def __init__(self, parent):
        super(CustomStyle, self).__init__(parent)

    def create_tv_style(self, name, heading_font=FONT, heading_bg=HEADING_BG, heading_fg=MAIN_FG, font=FONT,
                        rowheight=25, selectedfg='#262626', selectedbg=MAIN_FG):


        # heading layout
        try:
            self.element_create(f"{name}.Treeheading.border", "from", "default")
            self.layout(f"{name}.Treeview.Heading",
                        [(f"{name}.Treeheading.cell", {'sticky': 'nsew'}),
                         (f"{name}.Treeheading.border", {'sticky': 'nswe', 'children':
                             [(f"{name}.Treeheading.padding", {'sticky': 'nswe', 'children':
                                 [(f"{name}.Treeheading.image", {'side': 'right', 'sticky': ''}),
                                  (f"{name}.Treeheading.text", {'sticky': 'we'})]})]}), ])
        except tk.TclError:
            return f'{name}.Treeview'

        # heading style
        self.configure(f"{name}.Treeview.Heading",
                       font=heading_font,
                       background=heading_bg,
                       foreground=heading_fg
                       )

        # style
        self.configure(f"{name}.Treeview",
                       highlightthickness=0,
                       bd=0,
                       font=font,
                       rowheight=rowheight,
                       background=TV_BG,
                       foreground=MAIN_FG
                       )

        # layout
        self.layout(f"{name}.Treeview", [
            ('treeview.Treeview.treearea', {'sticky': 'news'})])

        # map
        self.map(f'{name}.Treeview',
                 background=[('disabled', '#262626'), ('selected', selectedbg)],
                 foreground=[('disabled', MAIN_FG), ('selected', selectedfg)],
                 relief=[('selected', 'flat')]
                 )

        return f'{name}.Treeview'


class Label(tk.Label):
    def __init__(self, parent, **kw):
        super(Label, self).__init__(parent)
        self.configure(
            bg='pink',
            fg=MAIN_FG,
            font=(FONT, 16, 'bold'),
        )
        self.config(**kw)


class ScrollFrame(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, **kw)
        self.y_list = [0, 0]
        self.scroll_units = 1
        self.config(relief='flat', borderwidth=0)
        self.canvas = tk.Canvas(self, borderwidth=0, relief='flat', highlightthickness=0, bg=self.cget('bg'))
        self.viewPort = tk.Frame(self.canvas, relief='flat', borderwidth=0, bg=self.cget('bg'))
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
