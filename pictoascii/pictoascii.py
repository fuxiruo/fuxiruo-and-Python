from PIL import Image
import argparse
import random

def get_char(pix):
    # 获取字符集的长度
    max_index = len(ascii_char)-1

    # 灰度值范围为 0-255，而字符集没有那么多
    # 需要进行如下处理才能将灰度值映射到指定的字符上
    unit = (255.0)/max_index

    # 返回灰度值对应的字符
    return ascii_char[int(pix/unit)]

parser = argparse.ArgumentParser()

parser.add_argument('file')
parser.add_argument('-o', '--output')
parser.add_argument('--width', type=int, default=80)
parser.add_argument('--height', type=int, default=80)

# 解析并获取参数
args = parser.parse_args()

# 输入的图片文件路径
IMG = args.file

# 输出字符画的宽度
WIDTH = args.width

# 输出字符画的高度
HEIGHT = args.height

# 输出字符画的路径
OUTPUT = args.output

'''
首先将 RGB 值转为灰度值，然后使用灰度值映射到字符列表中的某个字符。

下面是我们的字符画所使用的字符集，字符的种类与数量可以自己根据字符画的效果反复调试
'''
ascii_char = [ chr(x) for x in range(33, 127)]
ascii_char = random.sample(ascii_char, len(ascii_char))

if __name__ == '__main__':

    # 打开并调整图片的宽和高
    im = Image.open(IMG)
    im = im.resize((WIDTH,HEIGHT), Image.NEAREST)
    im = im.convert("L")

    # 初始化输出的字符串
    txt = ""

    # 遍历图片中的每一行
    for i in range(HEIGHT):
        # 遍历该行中的每一列
        for j in range(WIDTH):
            # 将 (j,i) 坐标的 RGB 像素转为字符后添加到 txt 字符串
            txt += get_char(im.getpixel((j,i)))
        # 遍历完一行后需要增加换行符
        txt += '\n'
    # 输出到屏幕
    print(txt)

    # 字符画输出到文件
    if OUTPUT:
        with open(OUTPUT,'w') as f:
            f.write(txt)
