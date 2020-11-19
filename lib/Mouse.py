import win32api
from time import sleep


class Mouse:
    @staticmethod
    def set_pos(x, y):
        win32api.SetCursorPos((x, y))

    @staticmethod
    def get_pos():
        return win32api.GetCursorPos()

    @staticmethod
    def wheel(clicks, x=None, y=None, interval=0.001):
        wheelturns = abs(clicks)
        if x and y:
            Mouse.set_pos(x, y)

        for _ in range(wheelturns):
            if clicks > 0:
                win32api.mouse_event(0x0800, 0, 0, -1, 0)
            elif clicks < 0:
                win32api.mouse_event(0x0800, 0, 0, 1, 0)
            sleep(interval)

    @staticmethod
    def left_click(x=None, y=None, lenght=0.005):
        if not x and not y:
            x, y = Mouse.get_pos()
        Mouse.set_pos(x, y)
        win32api.mouse_event(0x02, 0, 0, 0, 0)
        sleep(lenght)
        win32api.mouse_event(0x04, 0, 0, 0, 0)