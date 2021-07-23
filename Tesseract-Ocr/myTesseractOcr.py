import os
import tkinter
import tempfile
import tkinter.filedialog
from PIL import ImageGrab,Image
from time import sleep
import pytesseract


#用来显示全屏幕截图并响应二次截图的窗口类
class MyCapture:

    def __init__(self, png):
        self.result = None
        
        #变量X和Y用来记录鼠标左键按下的位置
        self.X = tkinter.IntVar(value=0)
        self.Y = tkinter.IntVar(value=0)

        #屏幕尺寸
        screenWidth = root.winfo_screenwidth()
        screenHeight = root.winfo_screenheight()

        #创建顶级组件容器
        self.top = tkinter.Toplevel(root, width=screenWidth, height=screenHeight)

        #不显示最大化、最小化按钮
        self.top.overrideredirect(True)

        self.canvas = tkinter.Canvas(self.top,bg='white', width=screenWidth, height=screenHeight)

        #显示全屏截图，在全屏截图上进行区域截图
        self.image = tkinter.PhotoImage(file=png)
        self.canvas.create_image(screenWidth//2, screenHeight//2, image=self.image)

        #鼠标左键按下的位置
        def onLeftButtonDown(event):

            self.X.set(event.x)

            self.Y.set(event.y)

            #开始截图
            self.sel = True

        self.canvas.bind('<Button-1>', onLeftButtonDown)

        #鼠标左键移动，显示选取的区域
        def onLeftButtonMove(event):

            if not self.sel:

                return

            global lastDraw

            try:
                #删除刚画完的图形，要不然鼠标移动的时候是黑乎乎的一片矩形
                self.canvas.delete(lastDraw)
            except Exception as e:
                pass

            lastDraw = self.canvas.create_rectangle(self.X.get(), self.Y.get(), event.x, event.y, outline='red')

        self.canvas.bind('<B1-Motion>', onLeftButtonMove)

        #鼠标右键取消
        def onRightButtonDown(event):
            #关闭当前窗口
            self.top.destroy()

        self.canvas.bind('<Button-3>', onRightButtonDown)
        
        #获取鼠标左键抬起的位置，保存区域截图
        def onLeftButtonUp(event):

            self.sel = False

            try:

                self.canvas.delete(lastDraw)

            except Exception as e:

                print(str(e))

            sleep(0.1)

            #考虑鼠标左键从右下方按下而从左上方抬起的截图
            left, right = sorted([self.X.get(), event.x])

            top, bottom = sorted([self.Y.get(), event.y])

            pic = ImageGrab.grab((left+1, top+1, right, bottom))

            #弹出保存截图对话框
            # fileName = tkinter.filedialog.asksaveasfilename(title='保存截图', filetypes=[('image', '*.jpg *.png')])

            # if fileName:
            #     pic.save(fileName)

            self.result = pic

            #关闭当前窗口
            self.top.destroy()

        self.canvas.bind('<ButtonRelease-1>', onLeftButtonUp)

        #让canvas充满窗口，并随窗口自动适应大小
        self.canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)

 #开始截图
def buttonCaptureClick():
    global t

    t.delete(0.0, tkinter.END)

    #最小化主窗口
    root.state('icon')

    sleep(0.2)

    tempFileFd, tempFileName = tempfile.mkstemp(suffix='.png')
    print(tempFileName)
    os.close(tempFileFd)

    #grab()方法默认对全屏幕进行截图
    im = ImageGrab.grab()

    im.save(tempFileName)

    im.close()

    #显示全屏幕截图
    w = MyCapture(tempFileName)

    buttonCapture.wait_window(w.top)

    if w.result:
        text = pytesseract.image_to_string(w.result, lang='chi_sim')
        t.insert('end', text)

    #截图结束，恢复主窗口，并删除临时的全屏幕截图文件
    root.state('normal')

    os.unlink(tempFileName)

""" 
注意：windows显示设置里的字体缩放不能开启，否则截出来的图可能不正常
"""
root = tkinter.Tk()
root.title('Tesseract-OCR')
#设置窗口大小与位置
root.geometry('400x200')

#设置窗口大小不可改变
root.resizable(False, False)

frameTop = tkinter.Frame(root, relief=tkinter.RIDGE, borderwidth=2)
frameTop.pack(fill=tkinter.X, expand=True)
buttonCapture = tkinter.Button(frameTop, text='识别', command=buttonCaptureClick)
# buttonCapture.place(x=10, y=10, width=80, height=20)
buttonCapture.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)

frameText = tkinter.Frame(root, relief=tkinter.RIDGE, borderwidth=2)
frameText.pack(fill=tkinter.BOTH, expand=1)
t = tkinter.Text(frameText, height=50)
t.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
scrollY = tkinter.Scrollbar(frameText)
scrollY.pack(side=tkinter.RIGHT, fill=tkinter.Y) # side是滚动条放置的位置，上下左右。fill是将滚动条沿着y轴填充
scrollY.config(command=t.yview) # 将文本框关联到滚动条上，滚动条滑动，文本框跟随滑动
t.config(yscrollcommand=scrollY.set) # 将滚动条关联到文本框

#启动消息主循环
root.mainloop()