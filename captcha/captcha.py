from PIL import Image
import hashlib
import time
import os
import math

work_path = os.path.split(os.path.realpath(__file__))[0]

# 向量计算
class VectorCompare:
    def magnitude(self,concordance):
        total = 0
        for word,count in concordance.items():
            total += count ** 2
        return math.sqrt(total)

    def relation(self,concordance1, concordance2):
        relevance = 0
        topvalue = 0
        for word, count in concordance1.items():
            if word in concordance2:
                topvalue += count * concordance2[word]
        return topvalue / (self.magnitude(concordance1) * self.magnitude(concordance2))

# 图片转换为向量
def buildvector(im):
    d1 = {}

    '''
    如果图像的模式是“1”，“L”，“P”等模式，因为这些模式是8bit表示一个像素，所以这些模式的颜色值的范围是在0~255，
    所以getdata（）的返回值的元素就不是上述的（R,G,B）的形式了，而是0~255中的任意一个数
    '''
    count = 0
    for i in im.getdata():# 这里其实是把每个像素点的颜色作为一个向量维度，也就是说只能识别相同尺寸大小相同字体的验证码图片
        d1[count] = i
        count += 1

    return d1

v = VectorCompare()


iconset = ['0','1','2','3','4','5','6','7','8','9','0','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

imageset = []

for letter in iconset:
    temp = []
    for img in os.listdir('{}/iconset/{}/'.format(work_path, letter)):
        if img != "Thumbs.db" and img != ".DS_Store": # windows check...
            img_file = "{}/iconset/{}/{}".format(work_path, letter, img)
            #print("{} add {}".format(letter, img_file))
            temp.append(buildvector(Image.open(img_file)))
    imageset.append({letter:temp})

im = Image.open("{}/captcha.gif".format(work_path))
im2 = Image.new("P",im.size,255)
im.convert("P")
temp = {}

for x in range(im.size[0]):
    for y in range(im.size[1]):
        pix = im.getpixel((x,y))
        temp[pix] = pix
        if pix == 220 or pix == 227: # these are the numbers to get
            im2.putpixel((x,y),0)

inletter = False
foundletter=False
start = 0
end = 0

letters = []

for x in range(im2.size[0]): # slice across
    for y in range(im2.size[1]): # slice down
        pix = im2.getpixel((x,y))
        if pix != 255:
            inletter = True

    if foundletter == False and inletter == True:
        foundletter = True
        start = x

    if foundletter == True and inletter == False:
        foundletter = False
        end = x
        letters.append((start,end))


    inletter=False

count = 0
for letter in letters:
    #print("{} letter ++++++++++++++++++++++++++++++".format(count))
    m = hashlib.md5()
    im3 = im2.crop(( letter[0] , 0, letter[1], im2.size[1]))

    guess = []

    for image in imageset:#imageset每个项都是一个字典
        for x,y in image.items(): #key为代表的字符，value是多张基准字符图片的向量
            #print("key {} len {}".format(x, len(y)))
            for yy in y:
                relation = v.relation(yy,buildvector(im3)) 
                guess.append((relation, x))

    guess.sort(reverse=True)
    print (guess[0])

    count += 1