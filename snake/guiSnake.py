import tkinter
import time
import logging
from collections import deque, namedtuple
from body import Body, BodyGeometry
from baseSnake import BaseSnake, Direction

class GuiSnake(BaseSnake):
    def __init__(self, master):
        "master是tkinter.Canvas类型，即蛇要显示的地方"
        super().__init__()
        self._master = master
        self._body_widgets = deque()
        self._foods = []
        self._food_widgets = {}
        self._direction = None

    def _creat_widget(self, body, color='white'):
        "在画布上增加身体块"
        topLeftX = body.geometry.x - body.geometry.w/2 
        topLeftY = body.geometry.y - body.geometry.h/2  
        bottomRightX = body.geometry.x + body.geometry.w/2 
        bottomRightY = body.geometry.y + body.geometry.h/2 
        rect = self._master.create_rectangle(topLeftX, topLeftY, bottomRightX, bottomRightY, fill=color)
        return rect       

    def _get_head(self):
        "获取头部的身体块"
        if self.bodys:
            return self.bodys[0]
        else:
            return None
    head = property(_get_head)
    
    def _get_foods_left(self):
        "获取剩余的食物块数量"
        return len(self._foods)
    foods_left = property(_get_foods_left)

    def _set_move_direction(self, direction):
        self._direction = direction

    def _get_move_direction(self):
        return self._direction
    move_direction = property(_get_move_direction, _set_move_direction)

    def _add_head(self, body, body_widget):    
        super().add_head(body)

        if self._body_widgets:
            self._master.itemconfig(self._body_widgets[0], fill='white')
        self._body_widgets.appendleft(body_widget)
        self._master.itemconfig(self._body_widgets[0], fill='red')
    
    def add_head(self, body):
        "增加身体块到头部"
        body_widget = self._creat_widget(body)
        self._add_head(body, body_widget)

    def _move_paint(self):
        for body, body_widget in zip(self._bodys, self._body_widgets):
            topLeftXNew = body.geometry.x - body.geometry.w/2 
            topLeftYNew = body.geometry.y - body.geometry.h/2  

            widgetSize = self._master.coords(body_widget)
            topLeftXOld = widgetSize[0]
            topLeftYOld = widgetSize[1]  

            self._master.move(body_widget, topLeftXNew-topLeftXOld, topLeftYNew-topLeftYOld)

    def move(self, direction, distance):
        "每次只移动一个身体的距离"
        total = 0
        step = max(self._bodys[0].geometry.w, self._bodys[0].geometry.h)

        while total < distance:
            total += step
            super().move(direction, step)   
            self.check_eat_food()            

        self._move_paint()

    def move_right(self, distance):
        self.move(Direction.RIGHT, distance)

    def move_down(self, distance):
        self.move(Direction.DOWN, distance)

    def _get_food_widget_dict_key(self, food):
        return '{},{}'.format(food.geometry.x, food.geometry.y)

    def try_produce_food(self, foodLimit, food):
        "food是Body对象，尝试在food位置产生食物, foodlimit限制最多存在的食物"
        if len(self._foods) >= foodLimit:
            # logging.debug('foods count limit, return')
            return False
        
        if food in self._foods:
            # logging.debug('food in foods, return')
            return False

        logging.debug('produec food on {},{}'.format(food.geometry.x, food.geometry.y))
        self._foods.append(food)
        widget = self._creat_widget(food, color='green')
        keys = self._get_food_widget_dict_key(food)
        self._food_widgets[keys] = widget
        
    def check_eat_food(self):
        "检查是否吃到了食物"
        head = self._bodys[0]
        for food in self._foods:
            if head.is_intersect(food):
                keys = self._get_food_widget_dict_key(food)
                food_widget = self._food_widgets[keys]
                del self._food_widgets[keys]

                # self._master.itemconfig(food_widget, color='white')
                self._add_head(food, food_widget)
                self._foods.remove(food)
                logging.debug('eat food on {},{}, now len {}'.format(food.geometry.x, food.geometry.y, len(self._bodys)))
                break

def example():
    windows = tkinter.Tk()
    windows.title('snake')
    windows.geometry('320x240')
    canvas = tkinter.Canvas(windows, bg='black', width=320, height=240)
    canvas.pack()

    snake = GuiSnake(canvas)

    bodyA = Body(BodyGeometry(15, 5, 10, 10))#10,0 
    bodyB = Body(BodyGeometry(25, 5, 10, 10))#20,0 
    bodyC = Body(BodyGeometry(35, 5, 10, 10))#30,0 
    bodyD = Body(BodyGeometry(45, 5, 10, 10))#40,0 
    snake.add_head(bodyA)
    snake.add_head(bodyB)
    snake.add_head(bodyC)
    snake.add_head(bodyD)

    def move(event):
        print(event.keysym)
        if 'Up' == event.keysym:
            snake.move_up(10)
        elif 'Down' == event.keysym:
            snake.move_down(10)
        elif 'Left' == event.keysym:
            snake.move_left(10)
        elif 'Right' == event.keysym:
            snake.move_right(10)

    windows.bind('<Up>', move)
    windows.bind('<Down>', move)
    windows.bind('<Left>', move)
    windows.bind('<Right>', move)

    windows.mainloop()

if __name__ == '__main__':
    example()