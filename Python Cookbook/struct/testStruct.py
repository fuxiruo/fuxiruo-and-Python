import struct
import unittest
import io

#1 简单的
class StructField:
    '''
    使用一个描述器来表示每个结构字段
    '''
    def __init__(self, format, offset):
        self._format = format
        self._offset = offset
    
    def __get__(self, instance, cls):
        '''
        Called to get the attribute of the owner class (class attribute access) or of an instance of that class (instance attribute access). owner is always the owner class, while instance is the instance that the attribute was accessed through, or None when the attribute is accessed through the owner. This method should return the (computed) attribute value or raise an AttributeError exception.
        '''
        if instance is None:
            return self
        else:
            r = struct.unpack_from(self._format, instance._buffer, self._offset)
            return r[0] if len(r)==1 else r 

    def __set__(self, instance, value):
        r = struct.unpack_from(self._format, instance._buffer, self._offset) #获取初始化时的数据类型
        originType = type(r[0] if len(r)==1 else r)
        if not isinstance(value, originType):
            raise TypeError('Excepted ' + str(originType))

        instance._buffer[self._offset:self._offset+struct.calcsize(self._format)] = struct.pack(self._format, value)

class Structure:
    def __init__(self, bytedatas):
        self._buffer = memoryview(bytedatas)

class PointXY(Structure):
    x = StructField('<i', 0) #x,int
    y = StructField('<i', 4) #y,int

# 2 通过元类自动生成StructField
class StructureMeta(type):
    '''
    元类
    '''
    def __init__(self, clsname, bases, clsdict):
        fileds = getattr(self, '_fileds_', [])
        byteOrder = ''
        offset = 0
        for fmt, filedName in fileds:
            if fmt.startswith(('<', '>', '!', '@')):
                byteOrder = fmt[0] #数据在内存中的格式，大端，小端等
                fmt = fmt[1:]
            fmt = byteOrder + fmt
            setattr(self, filedName, StructField(fmt, offset)) #自动根据_fileds_列表中的每一个元组生成字段
            offset += struct.calcsize(fmt) #自动计算下一个字段的偏移
        setattr(self, 'struct_size', offset) #结构体的总大小

class StructureWithMeta(metaclass=StructureMeta):
    def __init__(self, bytedatas):
        self._buffer = memoryview(bytedatas)

    @classmethod
    def from_file(cls, f):
        return cls(f.read(cls.struct_size))

class PointXYWithMeta(StructureWithMeta):
    _fileds_ = [
        ('<i', 'x'),
        ('i', 'y')          
    ]

class PointXYWithMeta2(StructureWithMeta):
    _fileds_ = [
        ('<i', 'x'),
        ('i', 'y'), 
        ('i', 'z')         
    ]

# 3 支持嵌套
class NestedStruct:
    '''
    嵌套字节结构
    '''
    def __init__(self, name, struct_type, offset):
        self._name = name
        self._struct_type = struct_type #NestedStructMeta 
        self._offset = offset

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            data = instance._buffer[self._offset:self._offset+self._struct_type.struct_size]
            result = self._struct_type(data) # 字节数组转换为NestedStructMeta
            setattr(instance, self._name, result)# 为了防止重复实例化，描述器保存了该实例中的内部结构对象
            return result

class NestedStructMeta(type):
    def __init__(self, clsname, bases, clsdict):
        fileds = getattr(self, '_fileds_', [])
        byteOrder = ''
        offset = 0
        for fmt, filedName in fileds:
            if isinstance(fmt, self.__class__):
                setattr(self, filedName, NestedStruct(filedName, fmt, offset))
                offset += fmt.struct_size    
            else: 
                if fmt.startswith(('<', '>', '!', '@')):
                    byteOrder = fmt[0] #数据在内存中的格式，大端，小端等
                    fmt = fmt[1:]
                fmt = byteOrder + fmt
                setattr(self, filedName, StructField(fmt, offset)) #自动根据_fileds_列表中的每一个元组生成字段
                offset += struct.calcsize(fmt) #自动计算下一个字段的偏移
        setattr(self, 'struct_size', offset) #结构体的总大小

class StructWithMeta(metaclass=NestedStructMeta):
    def __init__(self, bytedatas=None):
        if bytedatas is None:
            bytedatas = bytearray(self.struct_size)
        self._buffer = memoryview(bytedatas)

    def updateByteDatas(self, bytedatas):
        self._buffer = bytearray(bytedatas)

    def getByteDatas(self):
        return bytes(self._buffer)

class SinglePoint(StructWithMeta):
    _fileds_ = [
        ('<i', 'x'),
        ('i', 'y')          
    ]

class AllPoint(StructWithMeta):
    _fileds_ = [
        ('<i', 'tag'),
        (SinglePoint, 'min'),
        (SinglePoint, 'max')          
    ]

class StructTestCase(unittest.TestCase):
    def setUp(self):
        self._x = 16
        self._y = 34
        self._struct_size = struct.calcsize('<ii')
        self._bytesXY = struct.pack('<ii', self._x, self._y) #x和y小端模式转为4字节的16进制数组

    def test_point_xy(self):
        pointXY = PointXY(self._bytesXY)
        self.assertEqual(pointXY.x, self._x)
        self.assertEqual(pointXY.y, self._y)

    def test_StructureWithMeta(self):
        pointXY = PointXYWithMeta(self._bytesXY)
        self.assertEqual(pointXY.struct_size, self._struct_size) #通过StructureMeta自动计算的总长度
        self.assertEqual(pointXY.x, self._x)
        self.assertEqual(pointXY.y, self._y)

        pointXY2 = PointXYWithMeta2(self._bytesXY)
        self.assertNotEqual(pointXY2.struct_size, self._struct_size)

    def test_NestedStructMeta(self):
        tag = 2
        x1,y1 = 11,22
        x2,y2 = 44,55
        bytesdata = struct.pack('<iiiii', tag, x1, y1, x2, y2)
        size = struct.calcsize('<iiiii')

        allPoint = AllPoint(bytesdata)
        self.assertEqual(allPoint.struct_size, size)
        self.assertEqual(allPoint.tag, tag)
        self.assertEqual(allPoint.min.x, x1)
        self.assertEqual(allPoint.min.y, y1)
        self.assertEqual(allPoint.max.x, x2)
        self.assertEqual(allPoint.max.y, y2)

    def test_SetNestedStructMeta(self):
        allPoint = AllPoint()
        self.assertEqual(allPoint.tag, 0)

        with self.assertRaises(TypeError): # 'a'的类型跟allPoint.tag(int)不符合，应该要报错
            allPoint.tag = 'a' 
        self.assertEqual(allPoint.tag, 0)

        allPoint.tag = 1234 
        self.assertEqual(allPoint.tag, 1234)

    def test_NestedStructMeta_getByteDatas(self):
        tag = 2
        x1,y1 = 11,22
        x2,y2 = 44,55
        bytesdata = struct.pack('<iiiii', tag, x1, y1, x2, y2)
        size = struct.calcsize('<iiiii')

        allPoint = AllPoint()
        allPoint.tag = tag
        allPoint.min.x = x1
        allPoint.min.y = y1
        self.assertNotEqual(allPoint.getByteDatas(), bytesdata)
        allPoint.max.x = x2
        allPoint.max.y = y2
        self.assertEqual(allPoint.getByteDatas(), bytesdata)

        allPoint2 = AllPoint() # allPoint2 = AllPoint(bytesdata)构造出来的allPoint2.tag是只读的
        allPoint2.updateByteDatas(bytesdata)
        self.assertEqual(allPoint2.getByteDatas(), bytesdata)
        allPoint2.tag += 2
        self.assertNotEqual(allPoint2.getByteDatas(), bytesdata)

if __name__ == "__main__":
    unittest.main(verbosity=2)
    