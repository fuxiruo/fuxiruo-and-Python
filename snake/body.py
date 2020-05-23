from collections import namedtuple
from enum import Enum

class Direction(Enum):
    UP = 0
    DOWN = 1
    RIGHT = 2
    LEFT = 3

class BodyGeometry():
    def __init__(self, x, y, w, h):
        "(x,y)是中心坐标,w是宽，h是高"
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y and self.w == other.w and self.h == other.h:
            return True
        else:
            return False

    def is_intersect(self, other):
        "两个矩形区域是否有交叉"
        topLeftX = self.x - self.w/2 
        topLeftY = self.y - self.h/2  
        bottomRightX = self.x + self.w/2 
        bottomRightY = self.y + self.h/2 

        topLeftX2 = other.x - other.w/2 
        topLeftY2 = other.y - other.h/2   
        bottomRightX2 = other.x + other.w/2 
        bottomRightY2 = other.y + other.h/2 

        if (topLeftX<=topLeftX2<bottomRightX or topLeftX<bottomRightX2<=bottomRightX) \
            and (topLeftY<=topLeftY2<bottomRightY or topLeftY<bottomRightY2<=bottomRightY):
            return True
        else:
            return False

class Body():
    """构成蛇的身体块"""
    def __init__(self, geometry):
        self._geometry = geometry

    def __eq__(self, other):
        return self._geometry == other._geometry

    def _get_geometry(self):
        return self._geometry
    geometry = property(_get_geometry)
        
    def move_up(self, distance):
        self._geometry.y -= distance  

    def move_down(self, distance):
        self._geometry.y += distance 

    def move_left(self, distance):
        self._geometry.x -= distance

    def move_right(self, distance):
        self._geometry.x += distance

    def move_to_other(self, other):
        self._geometry.x = other._geometry.x
        self._geometry.y = other._geometry.y

    def move(self, direction, distance):
        if direction == Direction.UP:
            self.move_up(distance)
        elif direction == Direction.DOWN:
            self.move_down(distance)
        elif direction == Direction.LEFT:
            self.move_left(distance)
        elif direction == Direction.RIGHT:
            self.move_right(distance)

    def is_intersect(self, other):
        "判断两个身体块是否有重叠"
        return self.geometry.is_intersect(other.geometry)       

def example():
    body = Body(BodyGeometry(0, 0, 10, 10))
    print(body.geometry)

if __name__ == '__main__':
    example()