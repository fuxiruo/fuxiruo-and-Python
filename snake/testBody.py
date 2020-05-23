import unittest
from body import Body, BodyGeometry

class TestBody(unittest.TestCase):
    def setUp(self):
        self._x = 0
        self._y = 1
        self._w = 10
        self._h = 10
        self._body = Body(BodyGeometry(self._x, self._y, self._w, self._h))

    def test_geometry(self):
        self.assertEqual(self._body.geometry.x, self._x)
        self.assertEqual(self._body.geometry.y, self._y)
        self.assertEqual(self._body.geometry.w, self._w)
        self.assertEqual(self._body.geometry.h, self._h)

    def test_move(self):
        distance = 5

        prevX = self._body.geometry.x
        prevY = self._body.geometry.y
        prevW = self._body.geometry.w
        prevH = self._body.geometry.h
        self._body.move_up(distance)
        self.assertEqual(prevX, self._body.geometry.x)
        self.assertEqual(prevY-distance, self._body.geometry.y)
        self.assertEqual(prevW, self._body.geometry.w)
        self.assertEqual(prevH, self._body.geometry.h)

    def test_move_down(self):
        distance = 5

        prevX = self._body.geometry.x
        prevY = self._body.geometry.y
        prevW = self._body.geometry.w
        prevH = self._body.geometry.h
        self._body.move_down(distance)
        self.assertEqual(prevX, self._body.geometry.x)
        self.assertEqual(prevY+distance, self._body.geometry.y)
        self.assertEqual(prevW, self._body.geometry.w)
        self.assertEqual(prevH, self._body.geometry.h)

    def test_move_left(self):
        distance = 5

        prevX = self._body.geometry.x
        prevY = self._body.geometry.y
        prevW = self._body.geometry.w
        prevH = self._body.geometry.h
        self._body.move_left(distance)
        self.assertEqual(prevX-distance, self._body.geometry.x)
        self.assertEqual(prevY, self._body.geometry.y)
        self.assertEqual(prevW, self._body.geometry.w)
        self.assertEqual(prevH, self._body.geometry.h)

    def test_move_right(self):
        distance = 5

        prevX = self._body.geometry.x
        prevY = self._body.geometry.y
        prevW = self._body.geometry.w
        prevH = self._body.geometry.h
        self._body.move_right(distance)
        self.assertEqual(prevX+distance, self._body.geometry.x)
        self.assertEqual(prevY, self._body.geometry.y)
        self.assertEqual(prevW, self._body.geometry.w)
        self.assertEqual(prevH, self._body.geometry.h)

    def test_compare(self):
        bodyA = Body(BodyGeometry(0, 0, 10, 10))
        bodyB = Body(BodyGeometry(0, 0, 10, 10))
        bodyC = Body(BodyGeometry(10, 0, 10, 10))
        self.assertEqual(bodyA, bodyB)
        self.assertNotEqual(bodyB, bodyC)

    def test_is_intersect(self):
        bodyA = Body(BodyGeometry(15, 15, 10, 10))#10,10 20,20
        bodyB = Body(BodyGeometry(15, 15, 10, 10))

        bodyC = Body(BodyGeometry(15, 5, 10, 10))#10,0 20,10
        bodyD = Body(BodyGeometry(15, 25, 10, 10))#10,20 20,30
        bodyE = Body(BodyGeometry(5, 15, 10, 10))#0,10 10,20
        bodyF = Body(BodyGeometry(25, 15, 10, 10))#20,10 30,20

        bodyG = Body(BodyGeometry(15, 6, 10, 10))#10,1 20,11
        bodyH = Body(BodyGeometry(15, 24, 10, 10))#10,19 20,29
        bodyI = Body(BodyGeometry(6, 15, 10, 10))#1,10 11,20
        bodyJ = Body(BodyGeometry(24, 15, 10, 10))#19,10 29,20

        self.assertTrue(bodyA.is_intersect(bodyB))

        self.assertFalse(bodyA.is_intersect(bodyC))
        self.assertFalse(bodyA.is_intersect(bodyD))
        self.assertFalse(bodyA.is_intersect(bodyE))
        self.assertFalse(bodyA.is_intersect(bodyF))

        self.assertTrue(bodyA.is_intersect(bodyG))
        self.assertTrue(bodyA.is_intersect(bodyH))
        self.assertTrue(bodyA.is_intersect(bodyI))
        self.assertTrue(bodyA.is_intersect(bodyJ))

    def test_move_to_other(self):
        bodyA = Body(BodyGeometry(0, 0, 10, 10))
        bodyB = Body(BodyGeometry(10, 10, 10, 10))
        bodyA.move_to_other(bodyB)
        self.assertEqual(bodyA.geometry.x, bodyB.geometry.x)
        self.assertEqual(bodyA.geometry.y, bodyB.geometry.y)

if __name__ == '__main__':
    unittest.main(verbosity=2)
