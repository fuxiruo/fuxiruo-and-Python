#!/usr/bin/python3
# -*- coding: utf-8 -*-
from socket import *
import threading
import re
import sys
import getopt


# 扫描函数
def portScanner_1(host,port,openports):
    try:
        s = socket(AF_INET,SOCK_STREAM)   #创建套接字
        s.settimeout(1)
        s.connect((host,port))            #使用connect函数连接
        #print('[+] %d open' %port)
        openports.append(port)             #连接成功则将该端口添加至开放端口列表中
        s.close()
    except:
        pass

#多线程执行函数
def portScanner_2(ip ,portlist , openports = []):
    nloops = range(len(portlist))    #为每个要查询的端口所执行的函数创建一个进程
    threads = []
    for i in nloops:
        t = threading.Thread(target=portScanner_1,args=(ip,portlist[i],openports))
        threads.append(t)
    for i in nloops:
        threads[i].start()
    for i in nloops:
        threads[i].join()

#主函数
def main():
    openports = []
    portlist = []
    try:
        option,arg = getopt.getopt(sys.argv[1:],'h:p:')     #获取运行时导入的参数
        openport = []
        for opt,val in option:
            if opt in ('-h'):
                host = val
            elif opt in ('-p'):
                ports = val.split('-')
                start_port =ports[0]
                end_port = ports[1]
                                                            #数据处理
        for p in range(int(start_port),int(end_port)):
            portlist.append(p)

        #portScanner_2(host, portlist, openports)
        portScanner_2(host,portlist,openports)             #执行扫描函数
        #print(input_ip)
        print("        IP:" + host)                        #输出扫描结果
        print("Open Ports:" + str(openports))
    except ValueError as e:
        print("INPUT ERROR!!!")

if __name__ == '__main__':
    main()
