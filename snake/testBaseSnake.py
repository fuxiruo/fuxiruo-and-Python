import unittest
import copy
from collections import deque
from body import Body, BodyGeometry, Direction
from baseSnake import BaseSnake

"""
- 初始：
  12345
1 +++o

- 向右：
  12345
1  +++o

- 向下:
  12345
1   +++
2     o

- 向左:
  12345
1    ++ 
2    o+

- 向左:
  12345
1     + 
2   o++

- 向上:
  12345
1   o  
2   +++
"""
# 每跑一个测试方法，都是用一个新的TestBaseSnake对象，而不是用同一个
class TestBaseSnake(unittest.TestCase):
    def setUp(self):
        body1 = Body(BodyGeometry(1, 1, 0, 0))
        body2 = Body(BodyGeometry(2, 1, 0, 0))
        body3 = Body(BodyGeometry(3, 1, 0, 0))
        body4 = Body(BodyGeometry(4, 1, 0, 0))
        self._bodys = [body4, body3, body2, body1]
        self._baseSnake = BaseSnake()
        index = len(self._bodys)-1
        while index >= 0:
            #    self._baseSnake.add_head(self._bodys[index]) 这样添加到_baseSnake的body跟_bodys里面的body是相同的对象
            self._baseSnake.add_head(copy.deepcopy(self._bodys[index]))
            index -= 1

    def printSnake(self):
        n = 6
        print('\n', '*' * n)
        print(' ', end='')
        for i in range(n):
            print(i,end='')
        
        for j in range(n):
            print(j, end='')
            for i in range(n):
                index = 0
                while index < len(self._baseSnake.bodys):
                    body = self._baseSnake.bodys[index]
                    if body.geometry.x == i and body.geometry.y == j:
                        if index == 0:
                            print('o', end='')
                        else:
                            print('+', end='')
                        break
                    index += 1
                else:
                    print(' ', end='')
            print('')

        print('*' * n)

    def test_count(self):
        body = Body(BodyGeometry(15, 15, 10, 10))
        baseSnake = BaseSnake(body)
        count = 1
        self.assertEqual(count, baseSnake.count())

        body2 = Body(BodyGeometry(15, 15, 10, 10))
        baseSnake.add_head(body2)
        count += 1
        self.assertEqual(count, baseSnake.count())

    def test_is_move_able(self):
        body1 = Body(BodyGeometry(0, 1, 0, 0))
        body2 = Body(BodyGeometry(0, 2, 0, 0))
        body3 = Body(BodyGeometry(3, 0, 0, 0))
        body4 = Body(BodyGeometry(4, 0, 0, 0))

        # 头部在下，不能向上移动
        snakeHeadDown = BaseSnake()
        snakeHeadDown.add_head(body1)
        snakeHeadDown.add_head(body2)
        self.assertFalse(snakeHeadDown.is_movable(Direction.UP))
        self.assertTrue(snakeHeadDown.is_movable(Direction.DOWN))
        self.assertTrue(snakeHeadDown.is_movable(Direction.LEFT))
        self.assertTrue(snakeHeadDown.is_movable(Direction.RIGHT))

        # 头部在上，不能向下移动
        snakeHeadUp = BaseSnake()
        snakeHeadUp.add_head(body2)
        snakeHeadUp.add_head(body1)
        self.assertTrue(snakeHeadUp.is_movable(Direction.UP))
        self.assertFalse(snakeHeadUp.is_movable(Direction.DOWN))
        self.assertTrue(snakeHeadUp.is_movable(Direction.LEFT))
        self.assertTrue(snakeHeadUp.is_movable(Direction.RIGHT))

        # 头部在左，不能向右移动
        snakeHeadLeft = BaseSnake()
        snakeHeadLeft.add_head(body4)
        snakeHeadLeft.add_head(body3)
        self.assertTrue(snakeHeadLeft.is_movable(Direction.UP))
        self.assertTrue(snakeHeadLeft.is_movable(Direction.DOWN))
        self.assertTrue(snakeHeadLeft.is_movable(Direction.LEFT))
        self.assertFalse(snakeHeadLeft.is_movable(Direction.RIGHT))

        # 头部在右，不能向左移动
        snakeHeadRight = BaseSnake()
        snakeHeadRight.add_head(body3)
        snakeHeadRight.add_head(body4)
        self.assertTrue(snakeHeadRight.is_movable(Direction.UP))
        self.assertTrue(snakeHeadRight.is_movable(Direction.DOWN))
        self.assertFalse(snakeHeadRight.is_movable(Direction.LEFT))
        self.assertTrue(snakeHeadRight.is_movable(Direction.RIGHT))

    def test_move_right(self):
        # self.printSnake()

        index = len(self._bodys)-1
        while index > 0:
            self._bodys[index].move_to_other(self._bodys[index-1])
            index -= 1
        distance = 1
        self._bodys[0].move_right(distance)

        index = 0
        while index < len(self._bodys):
            self.assertNotEqual(self._bodys[index], self._baseSnake.bodys[index])
            index += 1

        self._baseSnake.move_right(distance)

        # self.printSnake()

        index = 0
        while index < len(self._bodys):
            self.assertEqual(self._bodys[index], self._baseSnake.bodys[index])
            index += 1
    
    def test_move_down(self):
        # self.printSnake()

        index = len(self._bodys)-1
        while index > 0:
            self._bodys[index].move_to_other(self._bodys[index-1])
            index -= 1
        distance = 1
        self._bodys[0].move_down(distance)

        index = 0
        while index < len(self._bodys):
            self.assertNotEqual(self._bodys[index], self._baseSnake.bodys[index])
            index += 1

        self._baseSnake.move_down(distance)

        # self.printSnake()

        index = 0
        while index < len(self._bodys):
            self.assertEqual(self._bodys[index], self._baseSnake.bodys[index])
            index += 1

    def test_move_left(self):
        # self.printSnake()

        index = len(self._bodys)-1
        while index > 0:
            self._bodys[index].move_to_other(self._bodys[index-1])
            index -= 1
        distance = 1
        self._bodys[0].move_left(distance)

        index = 0
        while index < len(self._bodys):
            self.assertNotEqual(self._bodys[index], self._baseSnake.bodys[index])
            index += 1

        self._baseSnake.move_left(distance)

        # self.printSnake()

        index = 0
        while index < len(self._bodys):
            self.assertEqual(self._bodys[index], self._baseSnake.bodys[index])
            index += 1

    def test_will_loopback(self):
        bodyA = Body(BodyGeometry(15, 5, 10, 10))#10,0 
        bodyB = Body(BodyGeometry(25, 5, 10, 10))#20,0 
        bodyC = Body(BodyGeometry(35, 5, 10, 10))#30,0 
        bodyD = Body(BodyGeometry(45, 5, 10, 10))#40,0 
        snake = BaseSnake()
        snake.add_head(bodyA)
        snake.add_head(bodyB)
        snake.add_head(bodyC)
        snake.add_head(bodyD)
        self.assertFalse(snake.is_will_loopback(Direction.DOWN, 10))
        snake.move_down(10)
        self.assertFalse(snake.is_will_loopback(Direction.LEFT, 10))
        snake.move_left(10)
        self.assertTrue(snake.is_will_loopback(Direction.UP, 10))

    def test_will_out_of_border(self):
        bodyA = Body(BodyGeometry(15, 5, 10, 10))#10,0 
        bodyB = Body(BodyGeometry(25, 5, 10, 10))#20,0 
        bodyC = Body(BodyGeometry(35, 5, 10, 10))#30,0 
        bodyD = Body(BodyGeometry(45, 5, 10, 10))#40,0 50,10
        snake = BaseSnake()
        snake.add_head(bodyA)
        snake.add_head(bodyB)
        snake.add_head(bodyC)
        snake.add_head(bodyD)
        self.assertFalse(snake.is_will_out_of_border(Direction.RIGHT, 10))
        self.assertFalse(snake.is_will_out_of_border(Direction.DOWN, 10))

        snake.set_border(0, 0, 50, 20)
        self.assertTrue(snake.is_will_out_of_border(Direction.RIGHT, 10))
        self.assertFalse(snake.is_will_out_of_border(Direction.DOWN, 10))

    def test_food_in_bodys(self):
        bodyA = Body(BodyGeometry(15, 5, 10, 10))#10,0 
        bodyB = Body(BodyGeometry(25, 5, 10, 10))#20,0 
        bodyC = Body(BodyGeometry(35, 5, 10, 10))#30,0 
        bodyD = Body(BodyGeometry(15, 5, 10, 10))#40,0 50,10

        bodys = deque()
        bodys.appendleft(bodyA)
        bodys.appendleft(bodyB)
        self.assertTrue(bodyA in bodys)
        self.assertFalse(bodyC in bodys)
        self.assertTrue(bodyD in bodys)

        bodys.remove(bodyA)
        self.assertFalse(bodyD in bodys)

    def test_nearest_body_distance(self):
        """
          12345
        1   +++ 
        2     +
        3    o+
        """
        body1 = Body(BodyGeometry(3, 1, 0, 0))
        body2 = Body(BodyGeometry(4, 1, 0, 0))
        body3 = Body(BodyGeometry(5, 1, 0, 0))
        body4 = Body(BodyGeometry(5, 2, 0, 0))
        body5 = Body(BodyGeometry(5, 3, 0, 0))
        body6 = Body(BodyGeometry(4, 3, 0, 0))
        snake = BaseSnake()
        snake.add_head(body1)
        snake.add_head(body2)
        snake.add_head(body3)
        snake.add_head(body4)
        snake.add_head(body5)
        snake.add_head(body6)

        distance, index = snake._nearest_body_distance(Direction.LEFT)
        self.assertEqual(distance, -1)
        distance, index = snake._nearest_body_distance(Direction.RIGHT)
        self.assertEqual(distance, 1)
        self.assertEqual(index, 1)
        distance, index = snake._nearest_body_distance(Direction.UP)
        self.assertEqual(distance, 2)
        self.assertEqual(index, 4)

    def test_will_dead_loop(self):
        """
          12345
        1   +++ 
        2   + +
        3   +o+
        """
        body1 = Body(BodyGeometry(3, 3, 1, 1))
        body2 = Body(BodyGeometry(3, 2, 1, 1))
        body3 = Body(BodyGeometry(3, 1, 1, 1))
        body4 = Body(BodyGeometry(4, 1, 1, 1))
        body5 = Body(BodyGeometry(5, 1, 1, 1))
        body6 = Body(BodyGeometry(5, 2, 1, 1))
        body7 = Body(BodyGeometry(5, 3, 1, 1))
        body8 = Body(BodyGeometry(4, 3, 1, 1))
        snake = BaseSnake()
        snake.add_head(body1)
        snake.add_head(body2)
        snake.add_head(body3)
        snake.add_head(body4)
        snake.add_head(body5)
        snake.add_head(body6)
        snake.add_head(body7)
        snake.add_head(body8)

        self.assertFalse(snake.is_will_dead_loop(Direction.DOWN))
        self.assertTrue(snake.is_will_dead_loop(Direction.UP))

# def suite():
#     suite = unittest.TestSuite()
#     suite.addTest(TestBaseSnake('test_count'))
#     suite.addTest(TestBaseSnake('test_is_move_able'))
#     suite.addTest(TestBaseSnake('test_move_right'))
#     suite.addTest(TestBaseSnake('test_move_down'))
#     suite.addTest(TestBaseSnake('test_move_left'))

#     return suite

# if __name__ == '__main__':
#     runner = unittest.TextTestRunner(verbosity=2)
#     runner.run(suite())

if __name__ == '__main__':
    unittest.main(verbosity=2)