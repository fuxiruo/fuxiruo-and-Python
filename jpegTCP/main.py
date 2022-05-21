import cv2
import numpy as np
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
import subprocess
from PIL import Image
from PIL import ImageTk
from enum import Enum, auto

import TcpPortScan

UDPport = 50050

LOG_FORMAT = '[%(asctime)s][%(levelname)5s][%(module)s:%(funcName)s][%(threadName)10s]->%(message)s'

class FaceDetectStatus(Enum):
    NO_FACE = auto()
    FACE_IN = auto()
    FACE_OUT = auto()
    FACE_RE_IN = auto()

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

ADB_PTAH = r"I:\android\android-studio\sdk\platform-tools\adb"

def adbSwipe():
    res = subprocess.Popen("{} shell input swipe 500 800 500 400".format(ADB_PTAH))
    return True

def adbPortAutoConnect(host):
    res = os.popen("{} devices".format(ADB_PTAH)).read()
    if res.find(host) > 0:
        logger.info("adb already connected succ")
        return

    portlist = []
    for p in range(38000, 45000):
        portlist.append(p)

    openports = []
    TcpPortScan.portScanner_2(host,portlist,openports)             #执行扫描函数
    # logger.info("IP:" + host)                        #输出扫描结果
    logger.info("Open Ports:" + str(openports))

    for port in openports:
        res = os.popen("{} connect {}:{}".format(ADB_PTAH, host, port)).read()
        logger.info(res)
        if res.find("connected") > 0:
            logger.info("adb connected succ")
            break

class tkGUI:
    def __init__(self, root):
        self.qu = tk.Button(root, text='Quit', command=self.endTCP, width=10)
        self.stop = tk.Button(root, text='Stop', command=self.stopShow, width=10)
        self.isStop = False
        self.save = tk.Button(root, text='Save pi', command=self.savePic, width=15)
        self.console = tk.Label(root, anchor='nw', font=(
            'Courier 10 Pitch', '11'), fg="white", bg="black", width=30, height=19)
        self.showData = tk.Label(root, anchor='w', font=(
            'Courier 10 Pitch', '11'), fg="orange", bg="black", width=30, height=7, justify='left')
        self.photo = tk.PhotoImage()
        self.image = tk.Label(root, image=self.photo, borderwidth=3)
        self.image.photo = self.photo
        self.currentPic = None

        self.stop.grid(row=0, column=0)
        self.save.grid(row=0, column=1)
        self.qu.grid(row=0, column=2)
        self.image.grid(rowspan=2, row=1, columnspan=2, padx=7, pady=5)
        self.console.grid(row=1, column=2, pady=2, padx=(0, 7), sticky=tk.N+tk.S+tk.W+tk.E)
        self.showData.grid(row=2, column=2, pady=2, sticky=tk.W+tk.E)
        root.grid_rowconfigure(1,weight=1)
        root.grid_columnconfigure(2,weight=1)

        self.root = root
        self.go = True
        self.displayThread = threading.Thread(target=self.waitConnection)
        self.displayThread.setDaemon(True)
        self.displayThread.start()

        self.lastPicTime = None
        self.nowPicTime = None
        self.threadShowing = False

        self.mLastFaceInTime = 0
        self.mLastFaceOutTime = 0
        self.mFaceDeteceStatus = FaceDetectStatus.NO_FACE

    def faceDetectState(self, bHadFace):
        lastStatus = self.mFaceDeteceStatus

        if  FaceDetectStatus.NO_FACE == self.mFaceDeteceStatus:
            if bHadFace:
                logger.info("bHadFace:{}, mFaceDeteceStatus:{}".format(bHadFace, self.mFaceDeteceStatus.name))
                self.mFaceDeteceStatus = FaceDetectStatus.FACE_IN
                self.mLastFaceInTime = time.time()
        elif FaceDetectStatus.FACE_IN == self.mFaceDeteceStatus:
            if not bHadFace:
                logger.info("bHadFace:{}, mFaceDeteceStatus:{}".format(bHadFace, self.mFaceDeteceStatus.name))
                self.mLastFaceOutTime = time.time()
                logger.info("{:.2f} - {:.2f} = {:.2f}".format(self.mLastFaceOutTime, self.mLastFaceInTime, self.mLastFaceOutTime - self.mLastFaceInTime))
                if self.mLastFaceOutTime - self.mLastFaceInTime > 0.7:
                    self.mFaceDeteceStatus = FaceDetectStatus.FACE_OUT
                elif self.mLastFaceOutTime - self.mLastFaceInTime > 0.5:
                    self.mFaceDeteceStatus = FaceDetectStatus.NO_FACE
        elif FaceDetectStatus.FACE_OUT == self.mFaceDeteceStatus:
            if bHadFace:
                logger.info("bHadFace:{}, mFaceDeteceStatus:{}".format(bHadFace, self.mFaceDeteceStatus.name))
                self.mLastFaceInTime = time.time()
                logger.info("{:.2f} - {:.2f} = {:.2f}".format(self.mLastFaceOutTime, self.mLastFaceInTime, time.time() - self.mLastFaceOutTime))
                if time.time() - self.mLastFaceOutTime > 0.7 and time.time() - self.mLastFaceOutTime < 3:
                    self.mFaceDeteceStatus = FaceDetectStatus.FACE_RE_IN
                elif time.time() - self.mLastFaceOutTime > 0.5:
                    self.mFaceDeteceStatus = FaceDetectStatus.FACE_IN

        if lastStatus != self.mFaceDeteceStatus:
            logger.info("{}->{}".format(lastStatus, self.mFaceDeteceStatus))

        if FaceDetectStatus.FACE_RE_IN == self.mFaceDeteceStatus:
            logger.info("mFaceDeteceStatus:{} !!!!!!!!!!!!!!!!!!!!!!!!!!".format(self.mFaceDeteceStatus.name))
            self.mFaceDeteceStatus = FaceDetectStatus.NO_FACE
            return True
        else:
            return False

    def updateFPS(self):
        self.nowPicTime = time.time()
        if self.lastPicTime:
            diff = self.nowPicTime - self.lastPicTime
            if diff > 0:
                fps = 1.0/diff
                self.showData["text"] = "FPS:{:.2f}".format(fps)
        self.lastPicTime = self.nowPicTime

    def waitConnection(self):
        # runs on a sepparate thread
        # HOST = "192.168.1.107"
        HOST = None
        PORT = 6666
        ROTATE = 90

        recvBuff = bytes()
        startFindIndex = 0

        while self.go:
            try:
                udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
                udps.bind(("", 5555))
                udps.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # 设置广播模式
                udps.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # 设置重复绑定
                while HOST is None:
                    logger.info("wait host broadcast ip")
                    data,addr = udps.recvfrom(1024)
                    logger.info("recv:{} from {}".format(data, addr))
                    if ord('@') == data[0] and ord('$') == data[len(data)-1]:
                        HOST = addr[0]
                        logger.info("find host ip:" + HOST)
                udps.close()

                adbPortAutoConnect(HOST)
            except Exception as e:
                logger.exception(e)
                break

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                try:
                    # Connect to server and send data
                    sock.settimeout(3)
                    sock.connect((HOST, PORT))
                    sock.settimeout(0.1)  # 设置超时
                    logger.debug("connect succ")
                    recvBuff = bytes()
                    startFindIndex = 0
                    picLen = 8
                    while self.go:
                        try:
                            data = sock.recv(204800)
                            if data:
                                # if 0==len(recvBuff):
                                #     logger.info('received {} startFindIndex:{}'.format(data[0:10].hex(' '), startFindIndex))
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
                                                    cvImg = cv2.imdecode(np.frombuffer(jpegBytes, np.uint8), cv2.IMREAD_COLOR)
                                                    cvImg = cv2.rotate(cvImg, cv2.ROTATE_90_COUNTERCLOCKWISE)
                                                    # # 用人脸级联分类器引擎进行人脸识别，返回的faces为人脸坐标列表，1.3是放大比例，3是重复识别次数
                                                    faces = face_cascade.detectMultiScale(cvImg, 1.1, 3, minSize=(90,90))
                                                    if  len(faces) > 0:
                                                        if self.faceDetectState(True):
                                                            sock.send(b'face rein')
                                                            if not adbSwipe():
                                                                adbPortAutoConnect(HOST)
                                                        for (x,y,w,h) in faces:
                                                            cv2.rectangle(cvImg,(x,y),(x+w,y+h),(255,0,0),2)
                                                        self.currentPic = Image.fromarray(cv2.cvtColor(cvImg, cv2.COLOR_BGR2RGB))
                                                    else:
                                                        self.faceDetectState(False)
                                                        pi = Image.open(picture_stream)
                                                        self.currentPic = pi.rotate(ROTATE, expand=True)
                                                    photo = ImageTk.PhotoImage(self.currentPic)
                                                    self.image.config(image=photo)
                                                    self.image.photo = photo

                                                recvBuff = recvBuff[jpegStartIndex4+5+picLen:]
                                                startFindIndex = 0
                                                picLen = 8
                                                logger.debug("end pic, curren recvBuff1: {}".format(len(recvBuff)))
                                                self.updateFPS()
                                            elif jpegStartIndex1 > 0:
                                                recvBuff = recvBuff[jpegStartIndex1:]
                                                startFindIndex = 0
                                                logger.warning("jpegStartIndex1:{}, curren recvBuff2: {}".format(jpegStartIndex1, len(recvBuff)))
                                            break
                                        else:
                                            logger.warning(recvBuff[0:5].hex(' '))
                                            logger.warning('bad index:{}, try next index:{}'.format(startFindIndex, jpegStartIndex2))
                                            startFindIndex = jpegStartIndex2
                                    except ValueError as e:
                                        # logger.warning(e)
                                        break
                                    except Exception as e:
                                        recvBuff = bytes()
                                        startFindIndex = 0
                                        picLen = 8
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
            filename = tkinter.filedialog.asksaveasfilename(title="Save As", filetypes=[("Pic Files", "*.jpg")], defaultextension=".jpg", initialdir=getCurrentPath(), initialfile=datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S"))#返回文件名
            if not filename:
                return
            self.currentPic.save(filename)

    def endTCP(self):
        logger.info("软件关闭")
        self.go = False
        self.root.destroy()

if __name__ == '__main__':
    xml_face = r"E:\Python\Python38\Lib\site-packages\cv2\data\haarcascade_frontalface_default.xml"
    # 导入人脸级联分类器引擎，'.xml'文件里包含训练出来的人脸特征，cv2.data.haarcascades即为存放所有级联分类器模型文件的目录
    face_cascade = cv2.CascadeClassifier(xml_face)

    root = tk.Tk()
    root.wm_title('JPEG TCP')
    app = tkGUI(root)
    root.protocol('WM_DELETE_WINDOW', app.endTCP)
    root.mainloop()
