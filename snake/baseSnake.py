import copy
from collections import deque
from body import Body, BodyGeometry, Direction

class BaseSnake():
    def __init__(self, body=None):
        """
        初始化时只有一块身体
        """
        self._bodys = deque()
        if body:
            self.add_head(body)

        self._borderTopLeftX = -9999
        self._borderTopLeftY = -9999
        self._borderBottomRightX = 9999
        self._borderBottomRightY = 9999

    def _get_bodys(self):
        return self._bodys
    bodys = property(_get_bodys)

    def set_border(self, topLeftX, topLeftY, bottomRightX, bottomRightY):
        "设置蛇活动的边界左上角和右下角"
        self._borderTopLeftX = topLeftX
        self._borderTopLeftY = topLeftY
        self._borderBottomRightX = bottomRightX
        self._borderBottomRightY = bottomRightY

    def add_head(self, body):
        self._bodys.appendleft(body)     

    def count(self):
        return len(self._bodys)
    
    def is_movable(self, direction):
        "头部跟头部的下一节在移动方向上有重叠，说明不能往这个方向移动"
        if len(self._bodys) < 2:
            return True
        head = self._bodys[0]
        next_body = self._bodys[1]

        if direction == Direction.UP:
            if head.geometry.x == next_body.geometry.x:
                if head.geometry.y > next_body.geometry.y:
                    return False
        elif direction == Direction.DOWN:
            if head.geometry.x == next_body.geometry.x:
                if head.geometry.y < next_body.geometry.y:
                    return False
        elif direction == Direction.LEFT:
            if head.geometry.y == next_body.geometry.y:
                if head.geometry.x > next_body.geometry.x:
                    return False
        elif direction == Direction.RIGHT:
            if head.geometry.y == next_body.geometry.y:
                if head.geometry.x < next_body.geometry.x:
                    return False

        return True

    def is_will_loopback(self, direction, distance):
        """
        检查回环，假设旧的头坐标为x1,y1，新的头坐标为x2,y2
        则检查头移动但身体还没移动时，其他身体的坐标是否在x1,x2,y1,y2形成的矩形区域上（可以当成一个巨大的身体块来看待）
        """
        if len(self._bodys) < 3:
            return True

        newHead = copy.deepcopy(self._bodys[0])
        newHead.move(direction, distance)

        oldHead = self._bodys[0]
        x = (newHead.geometry.x + oldHead.geometry.x)/2
        y = (newHead.geometry.y + oldHead.geometry.y)/2
        w = abs(newHead.geometry.x - oldHead.geometry.x) + newHead.geometry.w
        h = newHead.geometry.h
        hugeBody = Body(BodyGeometry(x, y, w, h))

        index = 2
        while index < len(self._bodys):
            if hugeBody.is_intersect(self._bodys[index]):
                return True
            index += 1

        return False

    def is_will_out_of_border(self, direction, distance):
        "检测是否会超出边界"
        newHead = copy.deepcopy(self._bodys[0])
        newHead.move(direction, distance)

        newTopLeftX = newHead.geometry.x - newHead.geometry.w/2 
        newTopLeftY = newHead.geometry.y - newHead.geometry.h/2  
        newBottomRightX = newHead.geometry.x + newHead.geometry.w/2 
        newBottomRightY = newHead.geometry.y + newHead.geometry.h/2 
        if newTopLeftX < self._borderTopLeftX or \
            newTopLeftY < self._borderTopLeftY or \
                newBottomRightX > self._borderBottomRightX or \
                    newBottomRightY > self._borderBottomRightY:
            return True

        return False

    def is_loopback(self, newHead):
        """
        检查回环，假设旧的头坐标为x1,y1，新的头坐标为x2,y2
        则检查头移动但身体还没移动时，其他身体的坐标是否在x1,x2,y1,y2形成的矩形区域上（可以当成一个巨大的身体块来看待）
        """
        if len(self._bodys) < 3:
            return True

        oldHead = self._bodys[1]
        x = (newHead.geometry.x + oldHead.geometry.x)/2
        y = (newHead.geometry.y + oldHead.geometry.y)/2
        w = abs(newHead.geometry.x - oldHead.geometry.x) + newHead.geometry.w
        h = newHead.geometry.h
        hugeBody = Body(BodyGeometry(x, y, w, h))

        index = 2
        while index < len(self._bodys):
            if hugeBody.is_intersect(self._bodys[index]):
                return False
            index += 1

        return True

    def is_dead_loop(self, distance):
        "是否已经死循环"
        for direction in Direction:
            if self.is_movable(direction):
                if (not self.is_will_out_of_border(direction, distance)) and (not self.is_will_loopback(direction, distance)):
                    return False
        else:
            return True

    def _nearest_body_distance(self, direction, newHead=None):
        "头部往direction方向移动，此方向上最近一个身体距离和index"
        """
        ++++++
        +
        +o
        例如o是头步，如果0向上移动，则此方向上最近一个身体距离就是2
        """
        if newHead:
            head = newHead
        else:
            head = self._bodys[0]

        index = 1
        nearest_distance = -1
        nearest_index = -1
        while index < len(self._bodys):
            distance = 0
            if self._bodys[index].geometry.x == head.geometry.x:# 垂直方向与头部坐标重合
                if direction == Direction.UP:
                    if self._bodys[index].geometry.y < head.geometry.y:
                        distance = head.geometry.y - self._bodys[index].geometry.y
                elif direction == Direction.DOWN:
                    if self._bodys[index].geometry.y > head.geometry.y:
                        distance = self._bodys[index].geometry.y - head.geometry.y
            elif self._bodys[index].geometry.y == head.geometry.y:# 水方向与头部坐标重合
                if direction == Direction.LEFT:
                    if self._bodys[index].geometry.x < head.geometry.x:
                        distance = head.geometry.x - self._bodys[index].geometry.x
                elif direction == Direction.RIGHT:
                    if self._bodys[index].geometry.x > head.geometry.x:
                        distance = self._bodys[index].geometry.x - head.geometry.x

            if distance > 0:
                if (nearest_distance < 0) or (distance < nearest_distance):
                    nearest_distance = distance
                    nearest_index = index
            
            index += 1

        # 没有身体则返回与边界的最近距离，nearest_index=-1
        if -1 == nearest_index:
            if direction == Direction.UP:
                nearest_distance = head.geometry.y - self._borderTopLeftY
                base_size = head.geometry.h
            elif direction == Direction.DOWN:
                nearest_distance = self._borderBottomRightY - head.geometry.y
                base_size = head.geometry.h
            elif direction == Direction.LEFT:
                nearest_distance = head.geometry.x - self._borderTopLeftX
                base_size = head.geometry.w
            elif direction == Direction.RIGHT:
                nearest_distance = self._borderBottomRightX - head.geometry.x
                base_size = head.geometry.w
            nearest_distance = nearest_distance//base_size*base_size
            
        return nearest_distance, nearest_index    

    def is_will_dead_loop(self, direction):
        """
        判断往方向direction移动后是否会死循环
        +++
        + +   
        +o
        例如o是头部，如果此时往上移动
        _nearest_body_distance得到的nearest_distance=2,nearest_index=4
        而此时的len(self._bodys)=7,(7-4-1) >= 2/self._bodys[index].geometry.y说明此时往上后下一步就不能往上运动了，也不能往下运动了
        再检查往上运动后是否还能往左右运动
        TODO：只预测了下一步，还是没能继续预测
        """
        nearest_distance, nearest_index = self._nearest_body_distance(direction)
        if direction == Direction.UP or direction == Direction.DOWN:
            size = self._bodys[0].geometry.h
        else:
            size = self._bodys[0].geometry.w
        if nearest_distance > 0:
            if len(self._bodys)-nearest_index-1 >= nearest_distance/size-1:
                # 假设o是头部，此时往上后下一步就不能往上或者下运动，模拟往上走上极限位，这样左右才有最大可能留出空位
                newHead = copy.deepcopy(self._bodys[0])
                newHead.move(direction, nearest_distance-size)

                if direction == Direction.UP or direction == Direction.DOWN:
                   next_direction1 = Direction.LEFT
                   next_direction2 = Direction.RIGHT
                   new_size = self._bodys[0].geometry.w
                else:
                   next_direction1 = Direction.UP
                   next_direction2 = Direction.DOWN
                   new_size = self._bodys[0].geometry.h
                next_nearest_distance1, next_nearest_index1 = self._nearest_body_distance(next_direction1, newHead)
                next_nearest_distance2, next_nearest_index2 = self._nearest_body_distance(next_direction2, newHead)

                # 头部到新的上下(左右)位置后，是否还能往左右(上下)移动
                # nearest_distance是头部和另一个的中心的距离，nearest_distance/new_size-1才是头部和另一个的空位距离
                # next_nearest_distance1/new_size-1也是同理，所以是减2
                if (len(self._bodys)-next_nearest_index1-1 >= \
                    (nearest_distance+next_nearest_distance1)/new_size-2) and \
                        (len(self._bodys)-next_nearest_index2-1 >= \
                            (nearest_distance+next_nearest_distance2)/new_size-2):
                    if -1 == next_nearest_index1 and -1 == next_nearest_index2:
                        return False
                    else:
                        return True

        return False

    def move(self, direction, distance):
        "头部移动后，其他的其实就是顶替上一个的位置"
        index = len(self._bodys)-1
        while index > 0:
            self._bodys[index].move_to_other(self._bodys[index-1])
            index -= 1

        self._bodys[0].move(direction, distance)

    def move_up(self, distance):
        self.move(Direction.UP, distance)

    def move_down(self, distance):
        self.move(Direction.DOWN, distance)

    def move_left(self, distance):
        self.move(Direction.LEFT, distance)

    def move_right(self, distance):
        self.move(Direction.RIGHT, distance)