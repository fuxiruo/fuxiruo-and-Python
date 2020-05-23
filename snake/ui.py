import tkinter
import threading
import time
import random
import logging
from guiSnake import GuiSnake
from body import Body, BodyGeometry, Direction
from setting import Setting

LOG_FORMAT = '[%(asctime)s][%(levelname)5s][%(threadName)10s:%(thread)5d][%(module)s:%(funcName)s]->%(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

def auto_move_thread():
    bNeedNewRandom = True
    nowStep = 0
    stepsToMove = 0
    foodLimit = 0
    speedLevel = 2
    while True:
        if snake.move_direction:#键盘控制移动
            d = snake.move_direction
            logging.debug(d)
        elif bNeedNewRandom:#随机自动控制移动
            bNeedNewRandom = False
            direction = random.choice([x.value for x in Direction])
            d = Direction(direction)
            stepsToMove = random.randint(10, 160)
            nowStep = 0
            logging.debug('move {} {} steps'.format(d.name, stepsToMove))

        if snake.foods_left == foodLimit:
            foodLimit = random.randint(1, 5)
            logging.debug('food limit {}'.format(foodLimit))

        produce_food(foodLimit)

        if snake.is_dead_loop(10):
            logging.warning('snake dead on len {}'.format(snake.count()))
            time.sleep(60)   
        elif not snake.is_movable(d):
            logging.debug('not able move '+d.name)
            bNeedNewRandom = True
        elif snake.is_will_loopback(d, 10):
            logging.debug('will loopback if move '+d.name)
            bNeedNewRandom = True
        elif snake.is_will_out_of_border(d, 10):
            logging.debug('will out of border if move '+d.name)
            bNeedNewRandom = True
        elif snake.is_will_dead_loop(d):
            logging.debug('will dead if move '+d.name)
            bNeedNewRandom = True
        else:
            if Direction.UP == d:
                snake.move_up(10)
            elif Direction.DOWN == d:
                snake.move_down(10)
            elif Direction.LEFT == d:
                snake.move_left(10)
            elif Direction.RIGHT == d:
                snake.move_right(10)
            time.sleep(0.25/speedLevel)        

        nowStep += 10
        if nowStep > stepsToMove:
            bNeedNewRandom = True

def move(event):
    if 'Up' == event.keysym:
        d = Direction.UP
    elif 'Down' == event.keysym:
        d = Direction.DOWN
    elif 'Left' == event.keysym:
        d = Direction.LEFT
    elif 'Right' == event.keysym:
        d = Direction.RIGHT
    
    snake.move_direction = d

def produce_food(foodLimit):
    x = random.randint(0, setting.screen_width-setting.size_of_snake)
    y = random.randint(0, setting.screen_height-setting.size_of_snake)
    # 生成的食物坐标中心与蛇身体的中心保持可以重合
    step = setting.size_of_snake
    x = (x//step) * step + step//2
    y = (y//step) * step + step//2
    food = Body(BodyGeometry(x, y, setting.size_of_snake, setting.size_of_snake))
    snake.try_produce_food(foodLimit, food)

setting = Setting()
windows = tkinter.Tk()
windows.title('snake')
windows.geometry(setting.screen_geometry)
canvas = tkinter.Canvas(windows, bg='black', width=setting.screen_width, height=setting.screen_height)
canvas.pack()

snake = GuiSnake(canvas)

bodyA = Body(BodyGeometry(15, 5, setting.size_of_snake, setting.size_of_snake))#10,0 
bodyB = Body(BodyGeometry(25, 5, setting.size_of_snake, setting.size_of_snake))#20,0 
bodyC = Body(BodyGeometry(35, 5, setting.size_of_snake, setting.size_of_snake))#30,0 
bodyD = Body(BodyGeometry(45, 5, setting.size_of_snake, setting.size_of_snake))#40,0 
snake.add_head(bodyA)
snake.add_head(bodyB)
snake.add_head(bodyC)
snake.add_head(bodyD)
snake.set_border(0, 0, setting.screen_width, setting.screen_height)

autoRunThread = threading.Thread(target=auto_move_thread, name='autoRun')
autoRunThread.setDaemon(True)
autoRunThread.start()

windows.bind('<Up>', move)
windows.bind('<Down>', move)
windows.bind('<Left>', move)
windows.bind('<Right>', move)

windows.mainloop()