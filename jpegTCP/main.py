from cmath import log
import struct
import time
import tkinter as tk
import threading
import socket
import logging
import io
import datetime
from PIL import Image
from PIL import ImageTk

UDPport = 50050

LOG_FORMAT = '[%(asctime)s][%(levelname)5s][%(module)s:%(funcName)s][%(threadName)10s]->%(message)s'

logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter(LOG_FORMAT)

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


class tkGUI:
    def __init__(self, root):
        self.qu = tk.Button(root, text='Quit', command=self.endTCP, width=10)
        self.console = tk.Label(root, anchor='nw', font=(
            'Courier 10 Pitch', '11'), fg="white", bg="black", width=60, height=19)
        self.showData = tk.Label(root, anchor='w', font=(
            'Courier 10 Pitch', '11'), fg="orange", bg="black", width=30, height=7, justify='left')
        self.showMatrix = tk.Label(root, anchor='nw', font=(
            'Courier 10 Pitch', '11'), fg="orange", bg="black", width=30, height=7, justify='left')
        self.photo = tk.PhotoImage()
        self.image = tk.Label(root, image=self.photo, borderwidth=3)
        self.image.photo = self.photo

        self.qu.grid(row=0, column=1)
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
                    while self.go:
                        try:
                            data = sock.recv(1000)
                            if data:
                                # print('received {}'.format(data.hex(' ')))
                                # logger.debug("parse start")
                                recvBuff += data

                                while startFindIndex < len(recvBuff):
                                    try:
                                        jpegStartIndex1 = recvBuff.index(0xaa, startFindIndex)
                                        jpegStartIndex2 = recvBuff.index(0x55, jpegStartIndex1)
                                        jpegStartIndex3 = recvBuff.index(0xaa, jpegStartIndex2)
                                        jpegStartIndex4 = recvBuff.index(0x55, jpegStartIndex3)
                                        if jpegStartIndex2 == jpegStartIndex1+1 and jpegStartIndex3 == jpegStartIndex2+1 and jpegStartIndex4 == jpegStartIndex3+1:
                                            # logger.debug("find header {}".format(
                                            #     recvBuff[jpegStartIndex1:jpegStartIndex1+4].hex()))

                                            if len(recvBuff) > jpegStartIndex4+4:
                                                picLen, = struct.unpack('>I', recvBuff[jpegStartIndex4+1:jpegStartIndex4+1+4])
                                                # logger.debug("lenght: {}".format(picLen))

                                            if len(recvBuff) >= jpegStartIndex4+5+picLen:
                                                # logger.debug("lenght: {}".format(picLen))
                                                # logger.debug("recv one {} start".format(recvBuff[jpegStartIndex4+5:jpegStartIndex4+5+3].hex()))
                                                # logger.debug("recv one {} end".format(recvBuff[jpegStartIndex4+5:jpegStartIndex4+5+picLen+10].hex(' ')))
                                                jpegBytes = recvBuff[jpegStartIndex4+5:jpegStartIndex4+5+picLen+1]
                                                # logger.debug("show {}".format(jpegBytes[0:4].hex()))

                                                # Convert bytes to stream (file-like object in memory)
                                                picture_stream = io.BytesIO(jpegBytes)
                                                # Create Image object
                                                pi = Image.open(picture_stream)
                                                pi = pi.rotate(ROTATE, expand=True)
                                                photo = ImageTk.PhotoImage(pi)
                                                self.image.config(image=photo)
                                                self.image.photo = photo
                                                recvBuff = recvBuff[jpegStartIndex4+5+picLen+1:]

                                                self.updateFPS()
                                            break
                                        else:
                                            startFindIndex = jpegStartIndex1+1
                                    except ValueError as e:
                                        # logger.warning(e)
                                        break
                                    except Exception as e:
                                        recvBuff = bytes()
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

                    logger.debug("程序关闭")
                    sock.close()
                except Exception as e:
                    logger.warning(str(e))
                    time.sleep(1)

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
