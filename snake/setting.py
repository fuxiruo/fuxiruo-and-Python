from collections import namedtuple

ScreenSize = namedtuple('ScreenSize', 'width, height')

class Setting():
    def __init__(self):
        self._screenSize = ScreenSize(240, 320)

    def _get_screen_geometry(self):
        return '{}x{}'.format(self._screenSize.width, self._screenSize.height)
    screen_geometry = property(_get_screen_geometry)

    def _get_screen_width(self):
        return self._screenSize.width
    screen_width = property(_get_screen_width)

    def _get_screen_height(self):
        return self._screenSize.height
    screen_height = property(_get_screen_height)

    def _get_snake_size(self):
        return 10
    size_of_snake = property(_get_snake_size)

def example():
    setting = Setting()
    print(setting.screen_geometry)

if __name__ == "__main__":
    example()
