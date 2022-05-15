from cmath import log
from inspect import isgetsetdescriptor
import struct
import time
import tkinter as tk
import tkinter.filedialog
import threading
import socket
import logging
import io
import datetime
import os
import sys
from PIL import Image
from PIL import ImageTk

UDPport = 50050

LOG_FORMAT = '[%(asctime)s][%(levelname)5s][%(module)s:%(funcName)s][%(threadName)10s]->%(message)s'

logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter(LOG_FORMAT)

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

def getCurrentPath():
    if getattr(sys, 'frozen', False):
        current_path = os.path.dirname(sys.executable)
    else:
        current_path = os.path.dirname(__file__)
    return current_path

class tkGUI:
    def __init__(self, root):
        self.qu = tk.Button(root, text='Quit', command=self.endTCP, width=10)
        self.stop = tk.Button(root, text='Stop', command=self.stopShow, width=10)
        self.isStop = False
        self.save = tk.Button(root, text='Save pi', command=self.savePic, width=15)
        self.console = tk.Label(root, anchor='nw', font=(
            'Courier 10 Pitch', '11'), fg="white", bg="black", width=60, height=19)
        self.showData = tk.Label(root, anchor='w', font=(
            'Courier 10 Pitch', '11'), fg="orange", bg="black", width=30, height=7, justify='left')
        self.showMatrix = tk.Label(root, anchor='nw', font=(
            'Courier 10 Pitch', '11'), fg="orange", bg="black", width=30, height=7, justify='left')
        self.photo = tk.PhotoImage()
        self.image = tk.Label(root, image=self.photo, borderwidth=3)
        self.image.photo = self.photo
        self.currentPic = None

        self.qu.grid(row=0, column=1)
        self.stop.grid(row=0, column=3)
        self.save.grid(row=0, column=4)
        self.image.grid(rowspan=2, row=1, columnspan=3, padx=7, pady=5)
        self.console.grid(columnspan=2, rowspan=1, row=1,
                          column=3, pady=2, padx=(0, 7))
        self.showData.grid(row=2, column=3, pady=2)
        self.showMatrix.grid(row=2, column=4, pady=2, padx=(2, 7))

        self.root = root
        self.go = True
        self.displayThread = threading.Thread(target=self.waitConnection)
        self.displayThread.setDaemon(True)
        self.displayThread.start()

        self.lastPicTime = None
        self.nowPicTime = None
        self.threadShowing = False

    def updateFPS(self):
        self.nowPicTime = time.time()
        if self.lastPicTime:
            diff = self.nowPicTime - self.lastPicTime
            fps = 1.0/diff
            self.showData["text"] = "FPS:{:.2f}".format(fps)
        self.lastPicTime = self.nowPicTime

    def waitConnection(self):
        # runs on a sepparate thread
        HOST = "192.168.1.104"
        PORT = 6666
        ROTATE = 90

        recvBuff = bytes()
        startFindIndex = 0

        while self.go:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                try:
                    # Connect to server and send data
                    sock.settimeout(3)
                    sock.connect((HOST, PORT))
                    sock.settimeout(0.1)  # 设置超时
                    logger.debug("connect succ")
                    recvBuff = bytes()
                    startFindIndex = 0
                    picLen = 0
                    while self.go:
                        try:
                            data = sock.recv(300000)
                            if data:
                                # print('received {}'.format(data.hex(' ')))
                                # logger.debug("parse start")
                                recvBuff += data

                                while len(recvBuff) > picLen and startFindIndex < len(recvBuff):
                                    try:
                                        jpegStartIndex1 = -1
                                        jpegStartIndex1 = recvBuff.index(0xaa, startFindIndex)
                                        jpegStartIndex2 = recvBuff.index(0x55, jpegStartIndex1)
                                        jpegStartIndex3 = recvBuff.index(0xaa, jpegStartIndex2)
                                        jpegStartIndex4 = recvBuff.index(0x55, jpegStartIndex3)
                                        if jpegStartIndex2 == jpegStartIndex1+1 and jpegStartIndex3 == jpegStartIndex2+1 and jpegStartIndex4 == jpegStartIndex3+1:
                                            if len(recvBuff) > jpegStartIndex4+4:
                                                picLen, = struct.unpack('>I', recvBuff[jpegStartIndex4+1:jpegStartIndex4+1+4])
                                                logger.debug("find header, pic lenght: {}, curren recvBuff: {}".format(picLen, len(recvBuff)))

                                            if len(recvBuff) >= jpegStartIndex4+5+picLen:
                                                logger.debug("find pic, pic lenght: {}, curren recvBuff: {}".format(picLen, len(recvBuff)))
                                                jpegBytes = recvBuff[jpegStartIndex4+5:jpegStartIndex4+5+picLen+1]

                                                if not self.isStop:
                                                    # Convert bytes to stream (file-like object in memory)
                                                    picture_stream = io.BytesIO(jpegBytes)
                                                    # Create Image object
                                                    pi = Image.open(picture_stream)
                                                    self.currentPic = pi.rotate(ROTATE, expand=True)
                                                    photo = ImageTk.PhotoImage(self.currentPic)
                                                    self.image.config(image=photo)
                                                    self.image.photo = photo

                                                recvBuff = recvBuff[jpegStartIndex4+5+picLen+1:]
                                                startFindIndex = 0
                                                picLen = 0
                                                logger.debug("end pic, curren recvBuff1: {}".format(len(recvBuff)))
                                                self.updateFPS()
                                            elif jpegStartIndex1 > 0:
                                                recvBuff = recvBuff[jpegStartIndex1:]
                                                startFindIndex = 0
                                                logger.warning("jpegStartIndex1:{}, curren recvBuff2: {}".format(jpegStartIndex1, len(recvBuff)))
                                            break
                                        else:
                                            logger.warning('bad index:{}, try next index:{}'.format(startFindIndex, jpegStartIndex2))
                                            startFindIndex = jpegStartIndex2
                                    except ValueError as e:
                                        # logger.warning(e)
                                        break
                                    except Exception as e:
                                        recvBuff = bytes()
                                        startFindIndex = 0
                                        picLen = 0
                                        logger.warning(e)

                                    # logger.debug("parse end")
                            else:
                                logger.debug("服务端关闭连接")
                                break
                        except socket.timeout:
                            pass
                        except Exception as e:
                            logger.exception(e)
                            break

                    sock.close()
                except Exception as e:
                    logger.warning(str(e))
                    time.sleep(1)

    def stopShow(self):
        self.isStop = not self.isStop
        if self.isStop:
            self.stop["text"] = "Resume"
        else:
            self.stop["text"] = "Stop"

    def savePic(self):
        if self.currentPic:
            filename = tkinter.filedialog.asksaveasfilename(title="Save As", filetypes=[("Pic Files", "*.jpg")], defaultextension=".jpg", initialdir=getCurrentPath(), initialfile=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))#返回文件名
            if not filename:
                return
            self.currentPic.save(filename)

    def endTCP(self):
        logger.debug("软件关闭")
        self.go = False
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    root.wm_title('JPEG TCP')
    app = tkGUI(root)
    root.protocol('WM_DELETE_WINDOW', app.endTCP)
    root.mainloop()
