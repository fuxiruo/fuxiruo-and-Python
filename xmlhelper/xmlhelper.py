import json
import os
import logging
import re
import shutil

import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk
import tkinter.constants as TC

from myhelper import myexcel, myxml, myui

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

def getCurrentPath():
    current_path = os.path.dirname(__file__)
    return current_path

def debugOnText(strLog):
    global t

    strLog += "\n"
    t.insert('end', strLog)

def reload_xml(file):
    if not file or not os.path.exists(file):
        return

    # 获取列表
    try:
        root = myxml.MyXml(file)

        comboboxModule['value'] = root.get_module_name_id_list()
        comboboxPort['value'], comboboxMotor['value'] = root.get_port_id_list()

        comboboxNewModule['value'] = comboboxModule['value']

    except Exception as Err:
        logger.exception('流程文件获取模组列表失败')
        tkinter.messagebox.showerror(title='流程文件获取模组列表失败', message=str(Err))

def on_xml_select():
    global config

    if "xmlDir" in config.keys():
        xmlDir = config["xmlDir"]
    else:
        xmlDir = ""

    file = tkinter.filedialog.askopenfilename(title="选择流程文件", filetypes=[("xml files", "*.xml")], initialdir=xmlDir)#返回文件名
    varXmlLabel.set(file)
    if file=='':
        return
    config["xmlFile"] = file
    config["xmlDir"] = os.path.dirname(varXmlLabel.get())

    # 获取列表
    reload_xml(file)

def _autoSetRowOfSheet(wb):
    try:
        comboboxRowOfMark.set('')
        comboboxRowOfChannel.set('')
        comboboxRowOfIO.set('')

        sheet1 = wb.sheet_by_name(comboboxSheet.get())

        for r in range(0, sheet1.nrows):
            if r > 3:
                break
            for c in range(0, sheet1.ncols):
                if sheet1.cell_value(r,c) and 1==sheet1.cell(r, c).ctype:
                    if '代号' in sheet1.cell_value(r,c):
                        comboboxRowOfMark.current(c)
                    elif '板号' in sheet1.cell_value(r,c):
                        comboboxRowOfChannel.current(c)
                    elif '信号' in sheet1.cell_value(r,c):
                        comboboxRowOfIO.current(c)

    except Exception as Err:
        logger.exception('_autoSetRowOfSheet失败')
        debugOnText(str(Err))

def reload_excel(file):
    if not file or not os.path.exists(file):
        return

    try:
        if '.xls' in file:
            me = myexcel.MyExcel(file)
            wb = me.workbook
            # for sheet in wb.sheet_names():
                # print(sheet)
            comboboxSheet['value'] = wb.sheet_names()
            comboboxSheet.current(0)
            for index, value in enumerate(wb.sheet_names()):
                if 'Sheet1' in value:
                    comboboxSheet.current(index)

            values = ["{}({})".format(i, chr(ord('A')+i)) for i in range(26)]
            comboboxRowOfChannel['value'] = values
            # comboboxRowOfChannel.current(3)
            comboboxRowOfMark['value'] = values
            # comboboxRowOfMark.current(10)
            comboboxRowOfIO['value'] = values
            # comboboxRowOfIO.current(6)

            _autoSetRowOfSheet(wb)
        else:
            comboboxSheet['value'] = []
            comboboxSheet.set("")

            # 获取列表
            root = myxml.MyXml(file)
            comboboxNewModule['value'] = root.get_module_name_id_list()

    except Exception as Err:
        logger.exception('获取工作表失败')
        tkinter.messagebox.showerror(title='获取工作表失败', message=str(Err))

def on_excel_select():
    global config

    if "excelDir" in config.keys():
        excelDir = config["excelDir"]
    else:
        excelDir = ""

    file = tkinter.filedialog.askopenfilename(title="选择端口分配文件", filetypes=[("excel files", "*.xls *.xlsx *.xml")], initialdir=excelDir)#返回文件名
    varExcelLabel.set(file)
    if file=='':
        return
    config["excelFile"] = file
    config["excelDir"] = os.path.dirname(varExcelLabel.get())

    reload_excel(varExcelLabel.get())

def onComboboxSheetSelected(event):
    me = myexcel.MyExcel(varExcelLabel.get())
    _autoSetRowOfSheet(me.workbook)

def on_change_switch():
    def get_func_replace(objectIDToChange, newSwitch):
        def func_repace(newLine):
            if newLine.find('ActionID="') > 0:
                indexOfStart = newLine.find('ObjID="')
                indexOfEnd = newLine.find('"', indexOfStart+len('ObjID="'))
                ObjID = newLine[indexOfStart+len('ObjID="'):indexOfEnd]

                if ObjID == objectIDToChange:
                    indexOfStart = newLine.find('MotorStatus="')
                    indexOfEnd = newLine.find('"', indexOfStart+len('MotorStatus="'))
                    MotorStatus = newLine[indexOfStart+len('MotorStatus="'):indexOfEnd]

                    # 判断限位
                    if MotorStatus=='1' or MotorStatus=='2':
                        debugOnText(dbgStr)
                        debugOnText(newLine)
                        debugOnText(dbgStr)
                        if newSwitch != '':
                            if newSwitch == '取反':
                                if MotorStatus=='1':
                                    newMotorStatus = '2'
                                else:
                                    newMotorStatus = '1'
                            elif newSwitch=='ON_A':
                                newMotorStatus = '1'
                            else:
                                newMotorStatus = '2'
                            oldStrt = 'MotorStatus="{}"'.format(MotorStatus)
                            newStrt = 'MotorStatus="{}"'.format(newMotorStatus)
                            newLine = newLine.replace(oldStrt, newStrt)

                        debugOnText('MotorStatus:' + MotorStatus)
                        debugOnText('newMotorStatus:' + newMotorStatus)
                        debugOnText(dbgStr2)
            return newLine
        return func_repace

    global t

    if not varXmlLabel.get() or not varOutputLabel.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择好文件!')
        return

    t.delete(0.0, TC.END)

    dbgStr = "*"*80
    dbgStr2 = "-"*80

    newXmlFile = varOutputLabel.get()
    xmlFile = varXmlLabel.get()

    if comboboxModule.get() != '':
        moduleIDToChange = comboboxModule.get()
        moduleIDToChange = moduleIDToChange.split('|')[1]
        debugOnText('只修改模组:' + comboboxModule.get())
    else:
        moduleIDToChange = None
        debugOnText('修改所有模组!')

    if comboboxMotor.get() != '':
        ObjectIDToChange = comboboxMotor.get()
        ObjectIDToChange = ObjectIDToChange.split('|')[1]
    else:
        tkinter.messagebox.showwarning(title='警告', message='请先选择好限位!')
        return

    myxml.MyXml.get_new_xml_replace_by_iter_line(xmlFile, newXmlFile, get_func_replace(ObjectIDToChange, comboboxSwitch.get()), moduleIDToChange)

def on_change_IOName():
    def get_func_replace(objectIDToChange, PortIONameToChange, PortCNameToChange, newIONameList):
        def func_repace(newLine):
            if newLine.find('ActionID="') > 0:
                indexOfStart = newLine.find('ObjID="')
                indexOfEnd = newLine.find('"', indexOfStart+len('ObjID="'))
                ObjID = newLine[indexOfStart+len('ObjID="'):indexOfEnd]

                if ObjID == objectIDToChange:
                    indexOfStart = newLine.find('ActionName="')
                    indexOfEnd = newLine.find('"', indexOfStart+len('ActionName="'))
                    ActionName = newLine[indexOfStart+len('ActionName="'):indexOfEnd]

                    if len(newIONameList) > 1:
                        PortIOName = newIONameList[0]
                        PortCName = newIONameList[1]
                        newActionName = ActionName.replace(PortIONameToChange, PortIOName)
                        newActionName = newActionName.replace(PortCNameToChange, PortCName)
                    else:
                        newActionName = ActionName.replace(PortIONameToChange,newIONameList[0])

                    oldStrt = 'ActionName="{}"'.format(ActionName)
                    newStrt = 'ActionName="{}"'.format(newActionName)
                    newLine = newLine.replace(oldStrt, newStrt)

                    debugOnText('ActionName:' + ActionName)
                    debugOnText('newActionName:' + newActionName)
                    debugOnText(dbgStr2)
            return newLine
        return func_repace

    global t

    if not varXmlLabel.get() or not varOutputLabel.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择好文件!')
        return

    t.delete(0.0, TC.END)

    # dbgStr = "*"*80
    dbgStr2 = "-"*80

    newXmlFile = varOutputLabel.get()
    xmlFile = varXmlLabel.get()

    if comboboxModule.get() != '':
        moduleIDToChange = comboboxModule.get()
        moduleIDToChange = moduleIDToChange.split('|')[1]
        debugOnText('只修改模组:' + comboboxModule.get())
    else:
        moduleIDToChange = None
        debugOnText('修改所有模组!')

    if comboboxPort.get() != '':
        sTemp = comboboxPort.get()
        PortIONameToChange = sTemp.split('|')[0]
        PortCNameToChange = sTemp.split('|')[1]
        ObjectIDToChange = sTemp.split('|')[2]
    else:
        tkinter.messagebox.showwarning(title='警告', message='请先选择好需要Port!')
        return

    myxml.MyXml.get_new_xml_replace_by_iter_line(xmlFile, newXmlFile, get_func_replace(ObjectIDToChange,PortIONameToChange,PortCNameToChange,varNewIOName.get().split('|')), moduleIDToChange)

def on_change_id():
    def get_func_replace(objectIDToChange, newID):
        def func_repace(newLine):
            #修改端口列表中的ObjectID
            oldObjectID = 'ObjectID="{}"'.format(objectIDToChange)
            newObjectID = 'ObjectID="{}"'.format(newID)
            if newLine.find(oldObjectID) > 0:
                newLine = newLine.replace(oldObjectID, newObjectID)
                debugOnText(newLine)
                debugOnText("-"*80)

            # 修改指定模组内动作的ObjID
            elif newLine.find('ActionID="') > 0:
                oldIDStr = 'ObjID="{}"'.format(objectIDToChange)
                newIDStr = 'ObjID="{}"'.format(newID)
                if newLine.find(oldIDStr) > 0:
                    newLine = newLine.replace(oldIDStr, newIDStr)
                    debugOnText(newLine)
                    debugOnText("-"*80)
            return newLine
        return func_repace

    global t

    if not varXmlLabel.get() or not varOutputLabel.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择好文件!')
        return

    t.delete(0.0, TC.END)

    newXmlFile = varOutputLabel.get()
    xmlFile = varXmlLabel.get()

    if comboboxModule.get() != '':
        moduleIDToChange = comboboxModule.get()
        moduleIDToChange = moduleIDToChange.split('|')[1]
        debugOnText('只修改模组:' + comboboxModule.get())
    else:
        moduleIDToChange = None
        debugOnText('修改所有模组!')

    if comboboxPort.get() != '':
        sTemp = comboboxPort.get()
        # PortIONameToChange = sTemp.split('|')[0]
        # PortCNameToChange = sTemp.split('|')[1]
        ObjectIDToChange = sTemp.split('|')[2]
    else:
        tkinter.messagebox.showwarning(title='警告', message='请先选择好需要Port!')
        return

    try:
        newID = int(varNewIOName.get())

        root = myxml.MyXml(varXmlLabel.get()).root

        port = root.find('.//*[@ObjectID="{}"]'.format(newID))
        if port is not None:
            tkinter.messagebox.showwarning(title='端口已经存在!', message=port.tag)
            return
    except Exception as Err:
        logger.exception('流程文件处理失败')
        tkinter.messagebox.showerror(title='流程文件处理失败', message=str(Err))
        return

    myxml.MyXml.get_new_xml_replace_by_iter_line(xmlFile, newXmlFile, get_func_replace(ObjectIDToChange, newID), moduleIDToChange)

def on_fix_IOName():
    def get_func_replace(oldObjectIDIONameMap, oldObjectIDCNameMap, ObjectIDIONameMap, ObjectIDCNameMap):
        def func_repace(newLine):
            if newLine.find('ActionID="') > 0:
                indexOfStart = newLine.find('ObjID="')
                indexOfEnd = newLine.find('"', indexOfStart+len('ObjID="'))
                ObjID = newLine[indexOfStart+len('ObjID="'):indexOfEnd]

                if ObjID in oldObjectIDIONameMap and ObjID in ObjectIDIONameMap:
                    PortIONameToChange = oldObjectIDIONameMap[ObjID]
                    PortCNameToChange = oldObjectIDCNameMap[ObjID]
                    PortIOName = ObjectIDIONameMap[ObjID]
                    PortCName = ObjectIDCNameMap[ObjID]

                    indexOfStart = newLine.find('ActionName="')
                    indexOfEnd = newLine.find('"', indexOfStart+len('ActionName="'))
                    ActionName = newLine[indexOfStart+len('ActionName="'):indexOfEnd]

                    # 替换动作中的端口标识和说明
                    newActionName = ActionName.replace(PortIONameToChange, PortIOName)
                    newActionName = newActionName.replace(PortCNameToChange, PortCName)

                    if newActionName != ActionName:
                        oldStrt = 'ActionName="{}"'.format(ActionName)
                        newStrt = 'ActionName="{}"'.format(newActionName)
                        newLine = newLine.replace(oldStrt, newStrt)

                        debugOnText('ActionName:' + ActionName)
                        debugOnText('newActionName:' + newActionName)
                        debugOnText("-"*80)
            return newLine
        return func_repace

    global t

    if not varXmlLabel.get() or not varExcelLabel.get() or not varOutputLabel.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择好文件!')
        return

    t.delete(0.0, TC.END)

    oldXmlFile = varExcelLabel.get()
    newXmlFile = varOutputLabel.get()
    xmlFile = varXmlLabel.get()

    if comboboxModule.get() != '':
        moduleIDToChange = comboboxModule.get()
        moduleIDToChange = moduleIDToChange.split('|')[1]
        debugOnText('只修改模组:' + comboboxModule.get())
    else:
        moduleIDToChange = None
        debugOnText('修改所有模组!')

    # 获取旧的xml的端口列表
    oldObjectIDIONameMap = {}
    oldObjectIDCNameMap = {}
    try:
        mx = myxml.MyXml(oldXmlFile)

        for port in mx.iter_port():
            oldObjectIDIONameMap[port.attrib['ObjectID']] = port.attrib['PortIOName']
            oldObjectIDCNameMap[port.attrib['ObjectID']] = port.attrib['PortCName']
    except Exception as Err:
        logger.exception('旧流程文件获取端口列表失败')
        tkinter.messagebox.showerror(title='旧流程文件获取端口列表失败', message=str(Err))
        return

    # 新的xml的端口列表
    ObjectIDIONameMap = {}
    ObjectIDCNameMap = {}
    for sTemp in comboboxPort['value']:
        PortIOName = sTemp.split('|')[0]
        PortCName = sTemp.split('|')[1]
        ObjectID = sTemp.split('|')[2]
        ObjectIDIONameMap[ObjectID] = PortIOName
        ObjectIDCNameMap[ObjectID] = PortCName

    myxml.MyXml.get_new_xml_replace_by_iter_line(xmlFile, newXmlFile, get_func_replace(oldObjectIDIONameMap, oldObjectIDCNameMap, ObjectIDIONameMap, ObjectIDCNameMap), moduleIDToChange)

def on_output_select():
    global varOutputLabel
    global config

    if "outputDir" in config.keys():
        outputDir = config["outputDir"]
    else:
        outputDir = ""

    file = tkinter.filedialog.asksaveasfilename(title="输出文件保存为", filetypes=[("xml files", "*.xml")], initialdir=outputDir)#返回文件名
    if file=='':
        return

    root,ext = os.path.splitext(file)
    if root and not ext:
        file += '.xml'
    config["outputFile"] = file
    config["outputDir"] = root

    varOutputLabel.set(file)

def on_copy_output_to_input():
    try:
        shutil.copyfile(varOutputLabel.get(), varXmlLabel.get())
        reload_xml(varXmlLabel.get())
        t.delete(0.0, TC.END)
        debugOnText('复制完毕')
    except Exception as Err:
        logger.exception('复制失败')
        tkinter.messagebox.showerror(title='输出文件覆盖输入文件失败', message=str(Err))

def on_verify_xml_and_excel():
    def get_func_replace(toDealActionList):
        def func_repace(newLine):
            if toDealActionList:
                indexPortIONameStart = newLine.find('PortIOName="')
                #裁剪出S3-S
                if indexPortIONameStart>0:
                    indexPortIONameEnd = newLine.find('"', indexPortIONameStart+len('PortIOName="'))
                    portIOName = newLine[indexPortIONameStart+len('PortIOName="'):indexPortIONameEnd]

                    if portIOName in dealActionList:
                        newLine = newLine.replace(dealActionList[portIOName]["OrigChannelID"], dealActionList[portIOName]["NewChannelID"])
                        newLine = newLine.replace(dealActionList[portIOName]["OrigIONum"], dealActionList[portIOName]["NewIONum"])
            return newLine
        return func_repace

    global varXmlLabel
    global varExcelLabel
    global varOutputLabel
    global t
    global comboboxSheet
    global config

    if not varXmlLabel.get() or not varExcelLabel.get() or not varOutputLabel.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择好文件!')
        return
    else:
        t.delete(0.0, TC.END)
        debugOnText(varXmlLabel.get())
        debugOnText(varExcelLabel.get())
        debugOnText(varOutputLabel.get())

        if not comboboxSheet.get():
            tkinter.messagebox.showwarning(title='警告', message='请先选择工作表!')
            return

    try:
        xmlRoot = myxml.MyXml(varXmlLabel.get())
        excelObj = myexcel.MyExcel(varExcelLabel.get())

        xmlFile = varXmlLabel.get()
        newXmlFile= varOutputLabel.get()
        xmlPortList = xmlRoot.get_portlist()
        excelPortList = excelObj.get_portlist(comboboxSheet.get(), comboboxRowOfChannel.current(), comboboxRowOfMark.current(), comboboxRowOfIO.current())

        if not xmlPortList or not excelPortList:
            tkinter.messagebox.showwarning(title='待处理列表为空', message='请检查文件或者工作表格式是否正确!')
            return

        dealPortList=[]
        dealActionList={}
        dbgStr = "*"*45+"PortList:"+"*"*45
        debugOnText(dbgStr)

        for portIOName,xmlPort in xmlPortList.items():
            if portIOName in excelPortList:
                excelPort = excelPortList[portIOName]
                dealPortList.append(portIOName)
                if (xmlPort["ChannelID"]==excelPort["ChannelID"]) and (xmlPort["IONum"]==excelPort["IONum"]):
                    dbgStr = "PortIOName:%15s, ChannelID:%s==%s IONum:%s==%s" % (portIOName, xmlPort["ChannelID"], excelPort["ChannelID"], xmlPort["IONum"], excelPort["IONum"])
                    debugOnText(dbgStr)
                else:
                    dbgStr = "+"*10 + "PortIOName:%15s, ChannelID:%s->%s IONum:%s->%s" % (portIOName, xmlPort["ChannelID"], excelPort["ChannelID"], xmlPort["IONum"], excelPort["IONum"]) + "+"*10
                    debugOnText(dbgStr)

                    if portIOName.startswith("M"):#电机的端口
                        debugOnText("注意：有电机端口更新，请手动修改对应pwm控制通道")

                    dealAction = {}
                    dealAction["PortIOName"] = "PortIOName=\"" + portIOName + "\""
                    dealAction["OrigChannelID"]= "ChannelID=\"" + xmlPort["ChannelID"] + "\""
                    dealAction["OrigIONum"]= "IONum=\"" + xmlPort["IONum"] + "\""
                    dealAction["NewChannelID"]= "ChannelID=\"" + excelPort["ChannelID"] + "\""
                    dealAction["NewIONum"]= "IONum=\"" + excelPort["IONum"] + "\""
                    dealActionList[portIOName] = dealAction

        myxml.MyXml.get_new_xml_replace_by_iter_line(xmlFile, newXmlFile, get_func_replace(dealActionList))

        for dealPort in dealPortList:
            del xmlPortList[dealPort]
            del excelPortList[dealPort]

        if not xmlPortList and not excelPortList:
            dbgStr = "All Port Had Done"
            debugOnText(dbgStr)
        else:
            debugOnText("*"*45 + "xmlPortList left:" + "*"*45)
            for portIOName,xmlPort in xmlPortList.items():
                debugOnText("PortIOName:%15s, ChannelID:%s IONum:%s" % (portIOName, xmlPort["ChannelID"], xmlPort["IONum"]))
            debugOnText("*"*45 + "excelPortList left:" + "*"*45)
            for portIOName,excelPort in excelPortList.items():
                debugOnText("PortIOName:%15s, ChannelID:%s IONum:%s" % (portIOName, excelPort["ChannelID"], excelPort["IONum"]))

        tkinter.messagebox.showinfo(title='成功', message='处理完成!')
    except Exception as Err:
        logger.exception('校对失败')
        tkinter.messagebox.showerror(title='失败', message=str(Err))

def check_data():
    try:
        mx = myxml.MyXml(varXmlLabel.get())

        for module in mx.iter_module():
            debugOnText("*"*45 + module.tag + "*"*45)
            for action in mx.find_action(module, objType=6): #数据赋值操作
                DataLocate = action.attrib['DataLocate']
                DateValue = action.attrib['DateValue']
                ActionName = action.attrib['ActionName']

                warnInfo = []
                actionNameShouldContain = ''
                if action.attrib['DateType'] == '1': #Int赋值
                    dataType = 'Int'
                    actionNameShouldContain += r'(I|i)(nt)?\s*' #正则I或者i开头，包含0或者1个nt，任意个\s即空格
                else:
                    dataType = 'Byte'
                    actionNameShouldContain += r'(B|b)(yte)?\s*'
                actionNameShouldContain += DataLocate
                if  re.search(actionNameShouldContain, ActionName) is None:
                    warnInfo.append("没有"+actionNameShouldContain)

                actionNameShouldContain = r'(=|＝)\s*{}(?:\D|$)'.format(DateValue)
                if  re.search(actionNameShouldContain, ActionName) is None:
                    warnInfo.append("没有"+actionNameShouldContain)

                if len(warnInfo)>0:
                    debugOnText("{actionTag} {actionName}<-->{dataType}{dataLocate}={dateValue}-->{warnInfo}".format(
                            actionTag=action.tag,
                            actionName=ActionName,
                            dataType=dataType,
                            dataLocate=DataLocate,
                            dateValue=DateValue,
                            warnInfo=';'.join(warnInfo)
                        ))

            debugOnText("\r\n"*3)

    except Exception as Err:
        logger.exception('流程文件处理失败')
        tkinter.messagebox.showerror(title='流程文件处理失败', message=str(Err))

def on_check_data():
    global varXmlLabel
    global t

    if not varXmlLabel.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择好脚本文件!')
    else:
        t.delete(0.0, TC.END)

        check_data()

def check_data_compare():
    try:
        mx = myxml.MyXml(varXmlLabel.get())

        for module in mx.iter_module():
            debugOnText("*"*45 + module.tag + "*"*45)
            for action in mx.find_action(module, objType=7): #数据比较操作
                DataLocate = action.attrib['DataLocate']
                DateValue = action.attrib['DateValue']
                ActionName = action.attrib['ActionName']
                DataComputer = action.attrib['DataComputer']

                warnInfo = []
                actionNameShouldContain = ''
                if action.attrib['DateType'] == '1': #Int赋值
                    dataType = 'Int'
                    actionNameShouldContain += r'(I|i)(nt)?\s*' #正则I或者i开头，包含0或者1个nt，任意个\s即空格
                else:
                    dataType = 'Byte'
                    actionNameShouldContain += r'(B|b)(yte)?\s*'
                actionNameShouldContain += DataLocate
                if  re.search(actionNameShouldContain, ActionName) is None:
                    warnInfo.append("没有"+actionNameShouldContain)

                actionNameShouldContain = ''
                computerMark = ''
                if DataComputer == '0': #<
                    actionNameShouldContain += '<'
                    computerMark = '<'
                elif DataComputer == '1':
                    actionNameShouldContain += '='
                    computerMark = '='
                else:
                    actionNameShouldContain += '>'
                    computerMark = '>'
                actionNameShouldContain += r'{}(?:\D|$)'.format(DateValue)
                if  re.search(actionNameShouldContain , ActionName) is None:
                    warnInfo.append("没有"+actionNameShouldContain)

                if len(warnInfo)>0:
                    debugOnText("{actionTag} {actionName}<-->{dataType}{dataLocate}{computerMark}{dateValue}?-->{warnInfo}".format(
                            actionTag=action.tag,
                            actionName=ActionName,
                            dataType=dataType,
                            dataLocate=DataLocate,
                            computerMark=computerMark,
                            dateValue=DateValue,
                            warnInfo=';'.join(warnInfo)
                        ))

            for action in mx.find_action(module, objType=17): #内存比较操作
                DataLocate = action.attrib['DataLocate']
                DataLocate2 = action.attrib['DataLocate2']
                ActionName = action.attrib['ActionName']
                DataComputer = action.attrib['DataComputer']

                warnInfo = []
                actionNameShouldContain = ''
                if action.attrib['DateType'] == '1': #Int赋值
                    dataType = 'Int'
                    actionNameShouldContain += r'(I|i)(nt)?\s*' #正则I或者i开头，包含0或者1个nt，任意个\s即空格
                else:
                    dataType = 'Byte'
                    actionNameShouldContain += r'(B|b)(yte)?\s*'
                tempActionName = actionNameShouldContain+r'{}(?:\D|$)'.format(DataLocate)
                if  re.search(tempActionName, ActionName) is None:
                    warnInfo.append("没有"+tempActionName)
                tempActionName = actionNameShouldContain+r'{}(?:\D|$)'.format(DataLocate2)
                if  re.search(tempActionName, ActionName) is None:
                    warnInfo.append("没有"+tempActionName)

                actionNameShouldContain = ''
                computerMark = ''
                if DataComputer == '0': #<
                    actionNameShouldContain += '<'
                    computerMark = '<'
                elif DataComputer == '1':
                    actionNameShouldContain += '='
                    computerMark = '='
                else:
                    actionNameShouldContain += '>'
                    computerMark = '>'
                if  ActionName.find(actionNameShouldContain)<0:
                    warnInfo.append("没有"+actionNameShouldContain)

                if len(warnInfo)>0:
                    debugOnText("{actionTag} {actionName}<-->{dataType}{dataLocate}{computerMark}{dataType}{dataLocate2}?-->{warnInfo}".format(
                            actionTag=action.tag,
                            actionName=ActionName,
                            dataType=dataType,
                            dataLocate=DataLocate,
                            computerMark=computerMark,
                            dataLocate2=DataLocate2,
                            warnInfo=';'.join(warnInfo)
                        ))

            debugOnText("\r\n"*3)

    except Exception as Err:
        logger.exception('流程文件处理失败')
        tkinter.messagebox.showerror(title='流程文件处理失败', message=str(Err))

def on_check_data_compare():
    global varXmlLabel
    global t

    if not varXmlLabel.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择好脚本文件!')
    else:
        t.delete(0.0, TC.END)

        check_data_compare()

def check_data_calc():
    try:
        mx = myxml.MyXml(varXmlLabel.get())

        for module in mx.iter_module():
            debugOnText("*"*45 + module.tag + "*"*45)
            for action in mx.find_action(module, objType=13): #自增自减
                DataLocate = action.attrib['DataLocate']
                DateValue = action.attrib['DateValue']
                ActionName = action.attrib['ActionName']

                warnInfo = []
                actionNameShouldContain = ''
                if action.attrib['DateType'] == '1': #Int
                    dataType = 'Int'
                    actionNameShouldContain += r'(I|i)(nt)?\s*' #正则I或者i开头，包含0或者1个nt，任意个\s即空格
                else:
                    dataType = 'Byte'
                    actionNameShouldContain += r'(B|b)(yte)?\s*'
                actionNameShouldContain += r'{}(?:\D|$)'.format(DataLocate)
                if  re.search(actionNameShouldContain, ActionName) is None:
                    warnInfo.append("没有"+actionNameShouldContain)

                actionNameShouldContain = ''
                computerMark = ''
                if DateValue == '0': #自增
                    actionNameShouldContain += '++'
                    computerMark = '++'
                else:
                    actionNameShouldContain += '--'
                    computerMark = '--'
                if  ActionName.find(actionNameShouldContain)<0:
                    warnInfo.append("没有"+actionNameShouldContain)

                if len(warnInfo)>0:
                    debugOnText("{actionTag} {actionName}<-->{dataType}{dataLocate}{computerMark} -->{warnInfo}".format(
                            actionTag=action.tag,
                            actionName=ActionName,
                            dataType=dataType,
                            dataLocate=DataLocate,
                            computerMark=computerMark,
                            warnInfo=';'.join(warnInfo)
                        ))

            for action in mx.find_action(module, objType=19): #数值计算
                DataLocate = action.attrib['DataLocate']
                DateValue = action.attrib['DateValue']
                DataLocate2 = action.attrib['DataLocate2']
                ActionName = action.attrib['ActionName']
                DataComputer = action.attrib['DataComputer']

                warnInfo = []
                actionNameShouldContain = ''
                if action.attrib['DateType'] == '1': #Int赋值
                    dataType = 'Int'
                    actionNameShouldContain += r'(I|i)(nt)?\s*' #正则I或者i开头，包含0或者1个nt，任意个\s即空格
                else:
                    dataType = 'Byte'
                    actionNameShouldContain += r'(B|b)(yte)?\s*'
                tempActionName = actionNameShouldContain+r'{}(?:\D|$)'.format(DataLocate)
                if  re.search(tempActionName, ActionName) is None:
                    warnInfo.append("没有"+tempActionName)
                tempActionName = actionNameShouldContain+r'{}(?:\D|$)'.format(DataLocate2)
                if  re.search(tempActionName, ActionName) is None:
                    warnInfo.append("没有"+tempActionName)
                tempActionName = actionNameShouldContain+r'{}='.format(DateValue)
                if  re.search(tempActionName, ActionName) is None:
                    warnInfo.append("没有"+tempActionName)

                actionNameShouldContain = ''
                computerMark = ''
                if DataComputer == '3': #+
                    actionNameShouldContain += '+'
                    computerMark = '+'
                elif DataComputer == '4':
                    actionNameShouldContain += '-'
                    computerMark = '-'
                elif DataComputer == '5':
                    actionNameShouldContain += '*'
                    computerMark = '*'
                elif DataComputer == '6':
                    actionNameShouldContain += '/'
                    computerMark = '/'
                elif DataComputer == '7':
                    actionNameShouldContain += '&'
                    computerMark = '&'
                elif DataComputer == '8':
                    actionNameShouldContain += '|'
                    computerMark = '|'
                else:
                    actionNameShouldContain += '?'
                    computerMark = '?'
                if  ActionName.find(actionNameShouldContain)<0:
                    warnInfo.append("没有"+actionNameShouldContain)

                if len(warnInfo)>0:
                    debugOnText("{actionTag} {actionName}<-->{dataType}{dateValue}={dataType}{dataLocate}{computerMark}{dataType}{dataLocate2} -->{warnInfo}".format(
                            actionTag=action.tag,
                            actionName=ActionName,
                            dataType=dataType,
                            dataLocate=DataLocate,
                            computerMark=computerMark,
                            dataLocate2=DataLocate2,
                            dateValue=DateValue,
                            warnInfo=';'.join(warnInfo)
                        ))

            debugOnText("\r\n"*3)

    except Exception as Err:
        tkinter.messagebox.showerror(title='流程文件处理失败', message=str(Err))

def on_check_data_calc():
    global varXmlLabel
    global t

    if not varXmlLabel.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择好脚本文件!')
    else:
        t.delete(0.0, TC.END)

        check_data_calc()

def check_encoder():
    try:
        mx = myxml.MyXml(varXmlLabel.get())

        for module in mx.iter_module():
            debugOnText("*"*45 + module.tag + "*"*45)
            for action in mx.find_action(module, 41): #清零编码器
                DataLocate = action.attrib['DataLocate']
                ActionName = action.attrib['ActionName']

                warnInfo = []
                actionNameShouldContain = r'(?:\D|^){}(?:\D|$)'.format(DataLocate) #假如DataBuf0=22，只匹配22，不匹配220，即22的前后都没有数字才行
                if  re.search(actionNameShouldContain, ActionName) is None:
                    warnInfo.append("通道不为"+str(DataLocate))

                if len(warnInfo)>0:
                    debugOnText("{actionTag} {actionName}<-->实际操作通道:{dataLocate}-->{warnInfo}".format(
                            actionTag=action.tag,
                            actionName=ActionName,
                            dataLocate=DataLocate,
                            warnInfo=';'.join(warnInfo)
                        ))

            actionNumList = [40,42]#读取编码器和读取原点偏移
            for num in actionNumList:
                for action in mx.find_action(module, num):
                    DataLocate = action.attrib['DataLocate']
                    DataBuf0 = action.attrib['DataBuf0']
                    ActionName = action.attrib['ActionName']

                    warnInfo = []
                    actionNameShouldContain = r'(?:\D|^){}(?:\D|$)'.format(DataBuf0) #假如DataBuf0=22，只匹配22，不匹配220，即22的前后都没有数字才行
                    if  re.search(actionNameShouldContain, ActionName) is None:
                        warnInfo.append("地址不为"+str(DataBuf0))

                    actionNameShouldContain = r'(?:\D|^){}(?:\D|$)'.format(DataLocate) #假如DataBuf0=22，只匹配22，不匹配220，即22的前后都没有数字才行
                    if  re.search(actionNameShouldContain, ActionName) is None:
                        warnInfo.append("通道不为"+str(DataLocate))

                    if len(warnInfo)>0:
                        debugOnText("{actionTag} {actionName}<-->读通道{dataLocate}到I{dataBuf0}-->{warnInfo}".format(
                                actionTag=action.tag,
                                actionName=ActionName,
                                dataLocate=DataLocate,
                                dataBuf0=DataBuf0,
                                warnInfo=';'.join(warnInfo)
                            ))

            debugOnText("\r\n"*3)

    except Exception as Err:
        logger.exception('流程文件处理失败')
        tkinter.messagebox.showerror(title='流程文件处理失败', message=str(Err))

def on_check_encoder():
    global varXmlLabel
    global t

    if not varXmlLabel.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择好脚本文件!')
    else:
        t.delete(0.0, TC.END)

        check_encoder()

def clear_unused_action():
    def get_func_replace(hadSearchAction):
        def func_repace(newLine):
            if newLine.find('ActionID="') > 0:
                indexOfStart = newLine.find('ActionID="')
                indexOfEnd = newLine.find('"', indexOfStart+len('ActionID="'))
                ActionID = newLine[indexOfStart+len('ActionID="'):indexOfEnd]

                indexOfStart = newLine.find('ModuleID="')
                indexOfEnd = newLine.find('"', indexOfStart+len('ModuleID="'))
                ModuleID = newLine[indexOfStart+len('ModuleID="'):indexOfEnd]

                indexOfStart = newLine.find('ObjType="')
                indexOfEnd = newLine.find('"', indexOfStart+len('ObjType="'))
                ObjType = newLine[indexOfStart+len('ObjType="'):indexOfEnd]

                if ModuleID in hadSearchAction:
                    if ObjType != '25': # 非注释
                        if not ActionID in hadSearchAction[ModuleID]:# 删除没有用到的动作
                            newLine = ""

                            debugOnText(newLine)
                            debugOnText("-"*80)

            return newLine
        return func_repace

    mx = myxml.MyXml(varXmlLabel.get())

    if comboboxModule.get() != '':
        moduleIDToChange = comboboxModule.get()
        moduleIDToChange = moduleIDToChange.split('|')[1]
        debugOnText('只修改模组:' + comboboxModule.get())
    else:
        moduleIDToChange = None
        debugOnText('修改所有模组!')

    hadSearchAction = mx.find_inconnection_action(moduleIDToChange=moduleIDToChange)

    newXmlFile = varOutputLabel.get()
    xmlFile = varXmlLabel.get()
    myxml.MyXml.get_new_xml_replace_by_iter_line(xmlFile, newXmlFile, get_func_replace(hadSearchAction), moduleIDToChange)

def on_clear_unused_action():
    global varXmlLabel
    global t

    if not varXmlLabel.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择好脚本文件!')
    else:
        t.delete(0.0, TC.END)

        clear_unused_action()

def mark_unused_action():
    def get_func_replace(hadSearchAction):
        def func_repace(newLine):
            if newLine.find('ActionID="') > 0:
                indexOfStart = newLine.find('ActionID="')
                indexOfEnd = newLine.find('"', indexOfStart+len('ActionID="'))
                ActionID = newLine[indexOfStart+len('ActionID="'):indexOfEnd]

                indexOfStart = newLine.find('ModuleID="')
                indexOfEnd = newLine.find('"', indexOfStart+len('ModuleID="'))
                ModuleID = newLine[indexOfStart+len('ModuleID="'):indexOfEnd]

                indexOfStart = newLine.find('ObjType="')
                indexOfEnd = newLine.find('"', indexOfStart+len('ObjType="'))
                ObjType = newLine[indexOfStart+len('ObjType="'):indexOfEnd]

                if ModuleID in hadSearchAction:
                    if ObjType != '25': # 非注释
                        if not ActionID in hadSearchAction[ModuleID]:
                            oldStrt = 'IsUse="True"'
                            newStrt = 'IsUse="False"'
                            newLine = newLine.replace(oldStrt, newStrt)

                            debugOnText(newLine)
                            debugOnText("-"*80)

            return newLine
        return func_repace

    mx = myxml.MyXml(varXmlLabel.get())

    if comboboxModule.get() != '':
        moduleIDToChange = comboboxModule.get()
        moduleIDToChange = moduleIDToChange.split('|')[1]
        debugOnText('只修改模组:' + comboboxModule.get())
    else:
        moduleIDToChange = None
        debugOnText('修改所有模组!')

    hadSearchAction = mx.find_inconnection_action(moduleIDToChange=moduleIDToChange)

    newXmlFile = varOutputLabel.get()
    xmlFile = varXmlLabel.get()
    myxml.MyXml.get_new_xml_replace_by_iter_line(xmlFile, newXmlFile, get_func_replace(hadSearchAction), moduleIDToChange)

def on_mark_unused_action():
    global varXmlLabel
    global t

    if not varXmlLabel.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择好脚本文件!')
    else:
        t.delete(0.0, TC.END)

        mark_unused_action()

def on_export_DevicesList():
    global t

    if not varXmlLabel.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择好文件!')
        return

    t.delete(0.0, TC.END)

    root = myxml.MyXml(varXmlLabel.get()).root

    for devicesList in root.iter('DevicesList'):
        for device in devicesList:
            debugOnText('{} {}'.format(device.attrib['DevId'], device.attrib['Client']))

def copy_module_to(dstXml):
    global config

    if not comboboxModule.get() or not comboboxNewModule.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择模组!')
        return

    if not varStartAction.get():
        tkinter.messagebox.showwarning(title='警告', message='请先设置参数!')
        return

    try:
        moduleIDToChange = comboboxModule.get().split('|')[1]
        newModuleID = comboboxNewModule.get().split('|')[1]
        mx = myxml.MyXml(varXmlLabel.get())
        toCopyAction = mx.find_inconnection_action(moduleIDToChange, varStartAction.get())[moduleIDToChange]
        mxother = myxml.MyXml(dstXml)
        unusedActionID = mxother.find_start_unused_actionID(newModuleID)

        newActionNo = int(unusedActionID)
        oldNewActionIDMap,needCopyLines = myxml.MyXml.get_old_action_id_to_new(varXmlLabel.get(), toCopyAction, moduleIDToChange, newActionNo)

        # 复制到新模组
        bNeedCopy = True
        bFindModuleStart = False
        bFindModuleEnd = False
        with open(varOutputLabel.get(), 'w') as newFileObj:
            with open(dstXml,encoding='gbk') as fileObj:
                for line in fileObj:
                    newLine = line

                    if bNeedCopy:
                        if not bFindModuleStart:
                            indexOfModuleStart = newLine.find('" ModuleID="{}"'.format(newModuleID))
                            if indexOfModuleStart > 0:
                                bFindModuleStart = True
                                # debugOnText('module start find:' + newLine)
                        elif bFindModuleStart and not bFindModuleEnd:
                            indexOfModuleStart = newLine.find('ModuleID="{}"'.format(newModuleID))
                            if indexOfModuleStart < 0:
                                bFindModuleEnd = True
                                # debugOnText('module end find:' + newLine)

                        # 在尾部增加自动复制的动作
                        if bFindModuleStart and bFindModuleEnd:
                            bNeedCopy = False
                            newActionNo = int(unusedActionID)
                            for copyLine in needCopyLines:
                                if newActionNo > 255:
                                    tkinter.messagebox.showerror(title='错误', message='ActionID超出255!')
                                    break
                                indexOfStart = copyLine.find('ActionID="')
                                indexOfEnd = copyLine.find('"', indexOfStart+len('ActionID="'))
                                actionNo = int(copyLine[indexOfStart+len('ActionID="'):indexOfEnd])

                                oldStrt = '<Action{:04d} ActionID="{}" ModuleID="{}"'.format(actionNo, actionNo, moduleIDToChange)
                                newStrt = '<Action{:04d} ActionID="{}" ModuleID="{}"'.format(newActionNo, newActionNo, newModuleID)
                                copyLine = copyLine.replace(oldStrt, newStrt)

                                indexOfStart = copyLine.find('DefaultAction="')
                                indexOfEnd = copyLine.find('"', indexOfStart+len('DefaultAction="'))
                                DefaultAction = copyLine[indexOfStart+len('DefaultAction="'):indexOfEnd]
                                oldStrt = 'DefaultAction="{}"'.format(DefaultAction)
                                newStrt = 'DefaultAction="{}"'.format(oldNewActionIDMap.get(DefaultAction, -1))
                                copyLine = copyLine.replace(oldStrt, newStrt)

                                indexOfStart = copyLine.find('IsTrue_NextAction="')
                                indexOfEnd = copyLine.find('"', indexOfStart+len('IsTrue_NextAction="'))
                                IsTrue_NextAction = copyLine[indexOfStart+len('IsTrue_NextAction="'):indexOfEnd]
                                oldStrt = 'IsTrue_NextAction="{}"'.format(IsTrue_NextAction)
                                newStrt = 'IsTrue_NextAction="{}"'.format(oldNewActionIDMap.get(IsTrue_NextAction, -1))
                                copyLine = copyLine.replace(oldStrt, newStrt)

                                indexOfStart = copyLine.find('IsFalse_NextActiton="')
                                indexOfEnd = copyLine.find('"', indexOfStart+len('IsFalse_NextActiton="'))
                                IsFalse_NextActiton = copyLine[indexOfStart+len('IsFalse_NextActiton="'):indexOfEnd]
                                oldStrt = 'IsFalse_NextActiton="{}"'.format(IsFalse_NextActiton)
                                newStrt = 'IsFalse_NextActiton="{}"'.format(oldNewActionIDMap.get(IsFalse_NextActiton, -1))
                                copyLine = copyLine.replace(oldStrt, newStrt)

                                indexOfStart = copyLine.find('PointX="')
                                indexOfEnd = copyLine.find('"', indexOfStart+len('PointX="'))
                                PointX = copyLine[indexOfStart+len('PointX="'):indexOfEnd]
                                newPointX = int(PointX) + int(varXOffset.get())
                                oldStrt = 'PointX="{}"'.format(PointX)
                                newStrt = 'PointX="{}"'.format(newPointX)
                                copyLine = copyLine.replace(oldStrt, newStrt)

                                indexOfStart = copyLine.find('PointY="')
                                indexOfEnd = copyLine.find('"', indexOfStart+len('PointY="'))
                                PointY = copyLine[indexOfStart+len('PointY="'):indexOfEnd]
                                newPointY = int(PointY) + int(varYOffset.get())
                                oldStrt = 'PointY="{}"'.format(PointY)
                                newStrt = 'PointY="{}"'.format(newPointY)
                                copyLine = copyLine.replace(oldStrt, newStrt)

                                debugOnText(copyLine)
                                newFileObj.write(copyLine)
                                newActionNo = newActionNo+1

                    newFileObj.write(newLine)
    except Exception as Err:
        logger.exception('复制失败')
        tkinter.messagebox.showerror(title='流程文件处理失败', message=str(Err))

def on_self_copy():
    global varXmlLabel
    global varOutputLabel
    global t
    global comboboxModule
    global config
    global varStartAction
    global varCountOfAction
    global varXOffset
    global varYOffset
    global varCountOfCopy

    if not varXmlLabel.get() or not varOutputLabel.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择好文件!')
        return

    if not comboboxModule.get() or not varStartAction.get() or not varCountOfAction.get() or not varXOffset.get() or not varYOffset.get():
        tkinter.messagebox.showwarning(title='警告', message='请先设置参数!')
        return

    t.delete(0.0, TC.END)
    debugOnText(varXmlLabel.get())
    debugOnText(varOutputLabel.get())

    dbgStr = "*"*80
    dbgStr2 = "-"*80

    newXmlFile = varOutputLabel.get()
    xmlFile = varXmlLabel.get()
    moduleIDToChange = comboboxModule.get().split('|')[1]
    bFindModuleStart = False
    bFindModuleEnd = False
    bFindStartAction = False
    bNeedCopy = True
    autoAddActionLines = []
    mx = myxml.MyXml(varXmlLabel.get())
    newStartActionID = mx.find_start_unused_actionID(moduleIDToChange)
    newActionNo = newStartActionID
    oldNewActionIDMap = {}
    with open(newXmlFile, 'w') as newFileObj:
        with open(xmlFile,encoding='gbk') as fileObj:
            for line in fileObj:
                newLine = line

                if bNeedCopy:
                    if not bFindModuleStart:
                        indexOfModuleStart = newLine.find('" ModuleID="{}"'.format(moduleIDToChange))
                        if indexOfModuleStart > 0:
                            bFindModuleStart = True
                            # debugOnText('module start find:' + newLine)
                            # debugOnText(dbgStr)
                    elif bFindModuleStart and not bFindModuleEnd:
                        indexOfModuleStart = newLine.find('ModuleID="{}"'.format(moduleIDToChange))
                        if indexOfModuleStart < 0:
                            bFindModuleEnd = True
                            # debugOnText('module end find:' + newLine)
                            # debugOnText(dbgStr)

                    if bFindModuleStart and not bFindStartAction:
                        indexOfAction = newLine.find('ActionID="{}"'.format(varStartAction.get()))
                        if indexOfAction > 0:
                            bFindStartAction = True
                            # debugOnText('action start find:' + newLine)
                            # debugOnText(dbgStr)

                    if bFindStartAction:
                        if len(autoAddActionLines) < int(varCountOfAction.get()):
                            indexOfStart = newLine.find('ActionID="')
                            indexOfEnd = newLine.find('"', indexOfStart+len('ActionID="'))
                            actionNo = newLine[indexOfStart+len('ActionID="'):indexOfEnd]
                            oldNewActionIDMap[actionNo] = newActionNo
                            debugOnText(str(actionNo) + "<->" + str(newActionNo))
                            autoAddActionLines.append(newLine)
                            newActionNo = newActionNo + 1

                    # 在尾部增加自动复制的动作
                    if bFindModuleStart and bFindModuleEnd:
                        bNeedCopy = False
                        for i in range(1, int(varCountOfCopy.get())+1):
                            noLine = 0
                            for addLine in autoAddActionLines:
                                noLine += 1

                                debugOnText(dbgStr)
                                debugOnText(addLine)
                                debugOnText(dbgStr)
                                indexOfStart = addLine.find('ActionID="')
                                indexOfEnd = addLine.find('"', indexOfStart+len('ActionID="'))
                                actionNo = addLine[indexOfStart+len('ActionID="'):indexOfEnd]
                                debugOnText('action No:' + actionNo)

                                indexOfStart = addLine.find('ActionName="')
                                indexOfEnd = addLine.find('"', indexOfStart+len('ActionName="'))
                                ActionName = addLine[indexOfStart+len('ActionName="'):indexOfEnd]
                                debugOnText('ActionName:' + ActionName)

                                indexOfStart = addLine.find('DataLocate="')
                                indexOfEnd = addLine.find('"', indexOfStart+len('DataLocate="'))
                                DataLocate = addLine[indexOfStart+len('DataLocate="'):indexOfEnd]
                                debugOnText('DataLocate:' + DataLocate)

                                indexOfStart = addLine.find('DateValue="')
                                indexOfEnd = addLine.find('"', indexOfStart+len('DateValue="'))
                                DateValue = addLine[indexOfStart+len('DateValue="'):indexOfEnd]
                                debugOnText('DateValue:' + DateValue)

                                indexOfStart = addLine.find('DataLocate2="')
                                indexOfEnd = addLine.find('"', indexOfStart+len('DataLocate2="'))
                                DataLocate2 = addLine[indexOfStart+len('DataLocate2="'):indexOfEnd]
                                debugOnText('DataLocate2:' + DataLocate2)

                                indexOfStart = addLine.find('PointX="')
                                indexOfEnd = addLine.find('"', indexOfStart+len('PointX="'))
                                PointX = addLine[indexOfStart+len('PointX="'):indexOfEnd]
                                debugOnText('PointX:' + PointX)

                                indexOfStart = addLine.find('PointY="')
                                indexOfEnd = addLine.find('"', indexOfStart+len('PointY="'))
                                PointY = addLine[indexOfStart+len('PointY="'):indexOfEnd]
                                debugOnText('PointY:' + PointY)

                                #开始替换
                                debugOnText(dbgStr2)
                                copyLine = addLine
                                indexOfStart = copyLine.find('DefaultAction="')
                                indexOfEnd = copyLine.find('"', indexOfStart+len('DefaultAction="'))
                                DefaultAction = copyLine[indexOfStart+len('DefaultAction="'):indexOfEnd]
                                newDefaultAction = int(oldNewActionIDMap.get(DefaultAction, -1))
                                if newDefaultAction != -1:
                                    newDefaultAction = newDefaultAction + (i-1)*int(varCountOfAction.get())
                                elif DefaultAction != -1:
                                    newDefaultAction = DefaultAction
                                debugOnText('DefaultAction:' + DefaultAction)
                                debugOnText('newDefaultAction:' + str(newDefaultAction))
                                oldStrt = 'DefaultAction="{}"'.format(DefaultAction)
                                newStrt = 'DefaultAction="{}"'.format(newDefaultAction)
                                copyLine = copyLine.replace(oldStrt, newStrt)

                                indexOfStart = copyLine.find('IsTrue_NextAction="')
                                indexOfEnd = copyLine.find('"', indexOfStart+len('IsTrue_NextAction="'))
                                IsTrue_NextAction = copyLine[indexOfStart+len('IsTrue_NextAction="'):indexOfEnd]
                                newIsTrue_NextAction = int(oldNewActionIDMap.get(IsTrue_NextAction, -1))
                                if newIsTrue_NextAction !=-1:
                                    newIsTrue_NextAction = newIsTrue_NextAction + (i-1)*int(varCountOfAction.get())
                                debugOnText('IsTrue_NextAction:' + IsTrue_NextAction)
                                debugOnText('newIsTrue_NextAction:' + str(newIsTrue_NextAction))
                                oldStrt = 'IsTrue_NextAction="{}"'.format(IsTrue_NextAction)
                                newStrt = 'IsTrue_NextAction="{}"'.format(newIsTrue_NextAction)
                                copyLine = copyLine.replace(oldStrt, newStrt)

                                indexOfStart = copyLine.find('IsFalse_NextActiton="')
                                indexOfEnd = copyLine.find('"', indexOfStart+len('IsFalse_NextActiton="'))
                                IsFalse_NextActiton = copyLine[indexOfStart+len('IsFalse_NextActiton="'):indexOfEnd]
                                newIsFalse_NextActiton = int(oldNewActionIDMap.get(IsFalse_NextActiton, -1))
                                if newIsFalse_NextActiton != -1:
                                    newIsFalse_NextActiton = newIsFalse_NextActiton + (i-1)*int(varCountOfAction.get())
                                debugOnText('IsFalse_NextActiton:' + IsFalse_NextActiton)
                                debugOnText('newIsFalse_NextActiton:' + str(newIsFalse_NextActiton))
                                oldStrt = 'IsFalse_NextActiton="{}"'.format(IsFalse_NextActiton)
                                newStrt = 'IsFalse_NextActiton="{}"'.format(newIsFalse_NextActiton)
                                copyLine = copyLine.replace(oldStrt, newStrt)

                                newActionNo = int(oldNewActionIDMap.get(actionNo, -1)) + (i-1)*int(varCountOfAction.get())
                                oldStrt = '<Action{:04d} ActionID="{}"'.format(int(actionNo), int(actionNo))
                                newStrt = '<Action{:04d} ActionID="{}"'.format(newActionNo, newActionNo)
                                copyLine = copyLine.replace(oldStrt, newStrt)

                                # 数据计算类型改变DataLocate和DefaultAction
                                if copyLine.find('ObjType="19"') > 0:
                                    newDataLocate = int(DataLocate) + i
                                    oldStrt = 'DataLocate="{}"'.format(DataLocate)
                                    newStrt = 'DataLocate="{}"'.format(newDataLocate)
                                    copyLine = copyLine.replace(oldStrt, newStrt)

                                    newDataLocate2 = int(DataLocate2) + i
                                    oldStrt = 'DataLocate2="{}"'.format(DataLocate2)
                                    newStrt = 'DataLocate2="{}"'.format(newDataLocate2)
                                    copyLine = copyLine.replace(oldStrt, newStrt)

                                    newActionName = re.sub(r'(\D|^){}(\D|$)'.format(DataLocate), r'\g<1>{}\g<2>'.format(newDataLocate), ActionName)
                                    newActionName = re.sub(r'(\D|^){}(\D|$)'.format(DataLocate2), r'\g<1>{}\g<2>'.format(newDataLocate2), newActionName)
                                    copyLine = copyLine.replace(ActionName, newActionName)
                                # 数据比较改变DataValue和IsTrue_NextAction和IsFalse_NextActiton
                                elif copyLine.find('ObjType="7"') > 0:
                                    newDateValue = int(DateValue) + i
                                    oldStrt = 'DateValue="{}"'.format(DateValue)
                                    newStrt = 'DateValue="{}"'.format(newDateValue)
                                    copyLine = copyLine.replace(oldStrt, newStrt)

                                    newActionName = re.sub(r'(\D|^){}(\D|$)'.format(DateValue), r'\g<1>{}\g<2>'.format(newDateValue), ActionName)
                                    copyLine = copyLine.replace(ActionName, newActionName)

                                    if newIsTrue_NextAction == -1:
                                        newIsTrue_NextAction = newStartActionID + i*int(varCountOfAction.get())
                                        oldStrt = 'IsTrue_NextAction="{}"'.format(IsFalse_NextActiton)
                                        newStrt = 'IsTrue_NextAction="{}"'.format(newIsTrue_NextAction)
                                        copyLine = copyLine.replace(oldStrt, newStrt)
                                        debugOnText('IsTrue_NextAction:' + IsTrue_NextAction)
                                        debugOnText('newIsTrue_NextAction:' + str(newIsTrue_NextAction))
                                        copyLine = copyLine.replace(oldStrt, newStrt)
                                    if newIsFalse_NextActiton == -1:
                                        newIsFalse_NextActiton = newStartActionID + i*int(varCountOfAction.get())
                                        oldStrt = 'IsFalse_NextActiton="{}"'.format(IsFalse_NextActiton)
                                        newStrt = 'IsFalse_NextActiton="{}"'.format(newIsFalse_NextActiton)
                                        copyLine = copyLine.replace(oldStrt, newStrt)
                                        debugOnText('IsFalse_NextActiton:' + IsFalse_NextActiton)
                                        debugOnText('newIsFalse_NextActiton:' + str(newIsFalse_NextActiton))
                                        copyLine = copyLine.replace(oldStrt, newStrt)

                                newPointX = int(PointX) + i*int(varXOffset.get())
                                oldStrt = 'PointX="{}"'.format(PointX)
                                newStrt = 'PointX="{}"'.format(newPointX)
                                copyLine = copyLine.replace(oldStrt, newStrt)

                                newPointY = int(PointY) + i*int(varYOffset.get())
                                oldStrt = 'PointY="{}"'.format(PointY)
                                newStrt = 'PointY="{}"'.format(newPointY)
                                copyLine = copyLine.replace(oldStrt, newStrt)

                                debugOnText(copyLine)
                                debugOnText(dbgStr2)

                                newFileObj.write(copyLine)

                newFileObj.write(newLine)

def on_copy_to_new_module():
    global config

    """指定开始序列，自动复制到结束，所以要先将需要复制的动作序列与其他序列断开连接"""
    if not varXmlLabel.get() or not varOutputLabel.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择好文件!')
        return
    else:
        t.delete(0.0, TC.END)
        debugOnText(varXmlLabel.get())
        debugOnText(varOutputLabel.get())

    copy_module_to(varXmlLabel.get())

def on_copy_to_other_xml():
    global config

    """指定开始序列，自动复制到结束，所以要先将需要复制的动作序列与其他序列断开连接"""
    if not varXmlLabel.get() or not varOutputLabel.get() or not varExcelLabel.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择好文件!')
        return
    else:
        t.delete(0.0, TC.END)
        debugOnText(varXmlLabel.get())
        debugOnText(varOutputLabel.get())
        debugOnText(varExcelLabel.get())

    copy_module_to(varExcelLabel.get())

def on_move_point_xy():
    def get_func_replace(toMoveAction):
        def func_repace(newLine):
            for actionToFind in toMoveAction:
                indexOfAction = newLine.find('ActionID="{}"'.format(actionToFind))
                if indexOfAction > 0:
                    indexOfStart = newLine.find('PointX="')
                    indexOfEnd = newLine.find('"', indexOfStart+len('PointX="'))
                    PointX = newLine[indexOfStart+len('PointX="'):indexOfEnd]
                    newPointX = int(PointX) + int(varXOffset.get())
                    oldStrt = 'PointX="{}"'.format(PointX)
                    newStrt = 'PointX="{}"'.format(newPointX)
                    newLine = newLine.replace(oldStrt, newStrt)

                    indexOfStart = newLine.find('PointY="')
                    indexOfEnd = newLine.find('"', indexOfStart+len('PointY="'))
                    PointY = newLine[indexOfStart+len('PointY="'):indexOfEnd]
                    newPointY = int(PointY) + int(varYOffset.get())
                    oldStrt = 'PointY="{}"'.format(PointY)
                    newStrt = 'PointY="{}"'.format(newPointY)
                    newLine = newLine.replace(oldStrt, newStrt)
                    toMoveAction.remove(actionToFind)
                    break
            return newLine
        return func_repace

    """指定开始序列，自动移动到结束，所以要先将需要移动的动作序列与其他序列断开连接"""
    if not varXmlLabel.get() or not varOutputLabel.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择好文件!')
        return
    else:
        t.delete(0.0, TC.END)
        debugOnText(varXmlLabel.get())

        if not comboboxModule.get():
            tkinter.messagebox.showwarning(title='警告', message='请先选择模组!')
            return

        if not varStartAction.get()  or not varXOffset.get() or not varYOffset.get():
            tkinter.messagebox.showwarning(title='警告', message='请先设置参数!')

    mx = myxml.MyXml(varXmlLabel.get())
    debugOnText(comboboxModule.get())
    moduleIDToChange = comboboxModule.get().split('|')[1]
    debugOnText(moduleIDToChange)
    toMoveAction = mx.find_inconnection_action(moduleIDToChange=moduleIDToChange, startAction=varStartAction.get())

    newXmlFile = varOutputLabel.get()
    xmlFile = varXmlLabel.get()
    myxml.MyXml.get_new_xml_replace_by_iter_line(xmlFile, newXmlFile, get_func_replace(toMoveAction[moduleIDToChange]), moduleIDToChange=moduleIDToChange)
    debugOnText(varOutputLabel.get())

def on_UI_select():
    global varUILabel
    global config

    if "UI_Dir" in config.keys():
        uiDir = config["UI_Dir"]
    else:
        uiDir = ""

    file = tkinter.filedialog.askdirectory(title="选择.ui文件夹", initialdir=uiDir)#返回文件名
    varUILabel.set(file)
    if file:
        config["UI_Dir"] = file

def deal_ui():
    allAddrList = {}
    for file in myui.MyUI.get_ui_files(varUILabel.get()):
        try:
            uiC = myui.MyUI(file)
            addrList = uiC.get_addrlist()

            if not addrList:
                # debugOnText('待处理列表为空')
                continue

            allAddrList.update(addrList)

            debugOnText(file)
            sortAddrList = sorted(addrList.values(), key=lambda addr: int(addr['RamAddr'])) #按地址排序
            for v in sortAddrList:
                debugOnText(str(v))
                debugOnText('-'*100)

            debugOnText('')

        except Exception as Err:
            logger.exception('处理失败')
            tkinter.messagebox.showerror(title='失败', message=str(Err))
            continue

    debugOnText('*'*100)
    sortAddrList = sorted(allAddrList.values(), key=lambda addr: int(addr['RamAddr'])) #按地址排序
    addrUsed = set()
    LabelComponentNameUsed = set()
    for v in sortAddrList:
        debugOnText(str(v))
        if 'RamAddr' in v:
            if v['RamAddr'] in addrUsed:
                debugOnText('地址重复!'*10)
            else:
                addrUsed.add(v['RamAddr'])
        if 'LabelComponentName' in v:
            if v['LabelComponentName'] in LabelComponentNameUsed:
                debugOnText('标签重复!'*10)
            else:
                LabelComponentNameUsed.add(v['LabelComponentName'])
        debugOnText('-'*100)

def deal_port():
    allPortList = []
    for file in myui.MyUI.get_ui_files(varUILabel.get()):
        try:
            uiC = myui.MyUI(file)
            portList = uiC.get_portlist()

            if not portList:
                # debugOnText('待处理列表为空')
                continue

            allPortList.extend(portList)

            debugOnText(file)
            # sortPortList = sorted(portList, key=lambda port: port['ID']) #按地址排序
            for v in portList:
                debugOnText(str(v))
                debugOnText('-'*100)

            debugOnText('')

        except Exception as Err:
            tkinter.messagebox.showerror(title='失败', message=str(Err))
            continue

    xml_port_list = None
    xml_id_as_key_port_list = None
    if varXmlLabel.get():
        mx = myxml.MyXml(varXmlLabel.get())
        xml_port_list = mx.get_portlist()
        xml_id_as_key_port_list = mx.get_portlist(bIdAsKey=True)

    debugOnText('*'*100)
    sortPortList = sorted(allPortList, key=lambda port: int(port['ID'])) #按地址排序
    for v in sortPortList:
        s_cmp_resutl = ''
        if xml_port_list:
            if v['Name'] in xml_port_list:
                if v['ID'] == xml_port_list[v['Name']]['ID']:
                    s_cmp_resutl = '='*10
                else:
                    s_cmp_resutl = '<->' + str(xml_port_list[v['Name']])
            elif v['ID'] in xml_id_as_key_port_list:
                s_cmp_resutl = '<->' + str(xml_id_as_key_port_list[v['ID']])
            else:
                s_cmp_resutl = '<->'
        debugOnText(str(v) + s_cmp_resutl)
        debugOnText('-'*100)

def on_deal_UI():
    global t
    global config

    if not varUILabel.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择好文件!')
    else:
        t.delete(0.0, TC.END)
        debugOnText(varUILabel.get())

        deal_ui()

def on_deal_UI_port():
    global t
    global config

    if not varUILabel.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择好文件!')
    else:
        t.delete(0.0, TC.END)
        debugOnText(varUILabel.get())

        deal_port()

def on_sysform_select():
    global varSysform
    global config

    if "Sysform_Dir" in config.keys():
        uiDir = config["Sysform_Dir"]
    else:
        uiDir = ""

    file = tkinter.filedialog.askopenfilename(title="选择sysform_kh.ui文件", filetypes=[("ui files", "*.ui")], initialdir=uiDir)#返回文件名
    varSysform.set(file)
    if file:
        config["Sysform_Dir"] = file

def deal_sysform_ui():
    try:
        uiC = myui.MyUI(varSysform.get())
        addrList = uiC.get_addrlist_from_sysform_ui()

        if not addrList:
            tkinter.messagebox.showwarning(title='待处理列表为空', message='请检查文件或者工作表格式是否正确!')
            return

        sortAddrList = sorted(addrList.values(), key=lambda addr: int(addr['RamAddr'])) #按地址排序
        for v in sortAddrList:
            debugOnText(str(v))

    except Exception as Err:
        logger.exception('处理失败')
        tkinter.messagebox.showerror(title='失败', message=str(Err))

def on_deal_sysform():
    global t
    global config

    if not varSysform.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择好文件!')
    else:
        t.delete(0.0, TC.END)
        debugOnText(varSysform.get())

        deal_sysform_ui()

def cb_radio_frame_change():
    t.delete(0.0, TC.END)
    frameText.pack_forget()
    if 'deal' in varFrameChange.get():
        frameUIDeal.pack_forget()
        frameAutoCopy.pack_forget()
        frameAutoDeal.pack(fill=TC.X, expand=True)
    elif 'copy' in varFrameChange.get():
        frameUIDeal.pack_forget()
        frameAutoDeal.pack_forget()
        frameAutoCopy.pack(fill=TC.X, expand=True)
    else:
        frameAutoCopy.pack_forget()
        frameAutoDeal.pack_forget()
        frameUIDeal.pack(fill=TC.X, expand=True)
    frameText.pack(fill=TC.BOTH, expand=True)

#GUI
#frameAutoDeal-tab0,frameAutoCopy-tab1,frameUI-tab2
windows = tkinter.Tk()
windows.geometry('1280x720')
windows.title('流程文件助手')

#frameXml
frameXml = tkinter.Frame(windows, relief=TC.RIDGE, borderwidth=2)
frameXml.pack(fill=TC.X, expand=1)
varXmlLabel = tkinter.StringVar()
xmlLabel = tkinter.Entry(frameXml, bg='white', textvariable=varXmlLabel)
xmlLabel.pack(side=TC.LEFT, fill=TC.X, expand=1)
xmlButton = tkinter.Button(frameXml, text="流程文件", command=on_xml_select)
xmlButton.pack(side=TC.RIGHT, ipadx=20)

frameExcel = tkinter.Frame(windows, relief=TC.RIDGE, borderwidth=2)
frameExcel.pack(fill=TC.X, expand=1)
varExcelLabel = tkinter.StringVar()
excelLabel = tkinter.Entry(frameExcel, bg='white', textvariable=varExcelLabel)
excelLabel.pack(side=TC.LEFT, fill=TC.X, expand=1)
excelButton = tkinter.Button(frameExcel, text="excel或流程文件", command=on_excel_select)
excelButton.pack(side=TC.LEFT, ipadx=8)
fixIONameButton = tkinter.Button(frameExcel, text="校正端口标识", command=on_fix_IOName)
fixIONameButton.pack(side=TC.LEFT, ipadx=20)
dealButton = tkinter.Button(frameExcel, text="校对excel", command=on_verify_xml_and_excel)
dealButton.pack(side=TC.LEFT, ipadx=45)

#frameOutput
frameOutput = tkinter.Frame(windows, relief=TC.RIDGE, borderwidth=2)
frameOutput.pack(fill=TC.X, expand=1)
varOutputLabel = tkinter.StringVar()
outputLabel = tkinter.Entry(frameOutput, bg='white', textvariable=varOutputLabel)
outputLabel.pack(side=TC.LEFT, fill=TC.X, expand=1)
outputButton = tkinter.Button(frameOutput, text="选择输出文件", command=on_output_select)
outputButton.pack(side=TC.RIGHT, ipadx=20)
copyButton = tkinter.Button(frameOutput, text="覆盖输入文件", command=on_copy_output_to_input)
copyButton.pack(side=TC.RIGHT, ipadx=20)

#frameModule
#模组不选则默认所有模组，否则只操作选中模组
frameModule = tkinter.Frame(windows, relief=TC.RIDGE, borderwidth=2)
frameModule.pack(fill=TC.X, expand=True)
moduleLabel = tkinter.Label(frameModule, text="模组", borderwidth=2)
moduleLabel.pack(side=TC.LEFT, ipadx=5)
# comboboxModule = tkinter.ttk.Combobox(frameModule, state="readonly")
comboboxModule = tkinter.ttk.Combobox(frameModule)
comboboxModule.pack(side=TC.LEFT, fill=TC.X, expand=True)
newModuleLabel = tkinter.Label(frameModule, text="Copy to模组", borderwidth=2)
newModuleLabel.pack(side=TC.LEFT, ipadx=5)
comboboxNewModule = tkinter.ttk.Combobox(frameModule, state="readonly")
comboboxNewModule.pack(side=TC.LEFT, fill=TC.X, expand=True)

#frameChange
frameChange = tkinter.Frame(windows, relief=TC.RIDGE, borderwidth=2, bg='black')
frameChange.pack(fill=TC.X, expand=True)
varFrameChange = tkinter.StringVar()
radioBtnAutoDeal = tkinter.Radiobutton(frameChange, text='自动处理', command=cb_radio_frame_change, variable=varFrameChange, value='autodeal', indicatoron=0, width=25, bg='gray')
radioBtnAutoDeal.pack(side=TC.LEFT)
radioBtnAutoCopy = tkinter.Radiobutton(frameChange, text='自动复制', command=cb_radio_frame_change, variable=varFrameChange, value='autocopy', indicatoron=0, width=25, bg='gray')
radioBtnAutoCopy.pack(side=TC.LEFT)
radioBtnDealUI = tkinter.Radiobutton(frameChange, text='.ui地址提取', command=cb_radio_frame_change, variable=varFrameChange, value='ui', indicatoron=0, width=25, bg='gray')
radioBtnDealUI.pack(side=TC.LEFT)
varFrameChange.set(radioBtnAutoDeal['value'])
tabLabel = tkinter.Entry(frameChange, bg='white', textvariable=varFrameChange, state="readonly")
tabLabel.pack(side=TC.LEFT, fill=TC.X, expand=1)

#frameAutoDeal
frameAutoDeal = tkinter.Frame(windows, relief=TC.RIDGE, borderwidth=2)
frameAutoDeal.pack(fill=TC.X, expand=True)
#frameAutoCopy
frameAutoCopy = tkinter.Frame(windows, relief=TC.RIDGE, borderwidth=2)
# frameAutoCopy.pack(fill=TC.X, expand=True)
#frameUI
frameUIDeal= tkinter.Frame(windows, relief=TC.RIDGE, borderwidth=2)
# frameUIDeal.pack(fill=TC.X, expand=True)

##frameSheet
frameSheet = tkinter.Frame(frameAutoDeal, relief=TC.RIDGE, borderwidth=2)
frameSheet.pack(fill=TC.X, expand=True)
sheetLabel = tkinter.Label(frameSheet, text="工作表", borderwidth=2)
sheetLabel.pack(side=TC.LEFT, ipadx=5)
comboboxSheet = tkinter.ttk.Combobox(frameSheet, state="readonly")
comboboxSheet.pack(side=TC.LEFT, fill=TC.X, expand=True)
comboboxSheet.bind("<<ComboboxSelected>>", onComboboxSheetSelected)
rowOfChannelLabel = tkinter.Label(frameSheet, text="通道组合所在列", borderwidth=2)
rowOfChannelLabel.pack(side=TC.LEFT, ipadx=5)
comboboxRowOfChannel = tkinter.ttk.Combobox(frameSheet, state="readonly")
comboboxRowOfChannel.pack(side=TC.LEFT, fill=TC.X, expand=True)
rowOfMarkLabel = tkinter.Label(frameSheet, text="标号所在列", borderwidth=2)
rowOfMarkLabel.pack(side=TC.LEFT, ipadx=5)
comboboxRowOfMark = tkinter.ttk.Combobox(frameSheet, state="readonly")
comboboxRowOfMark.pack(side=TC.LEFT, fill=TC.X, expand=True)
rowOfIOLabel = tkinter.Label(frameSheet, text="IO所在列", borderwidth=2)
rowOfIOLabel.pack(side=TC.LEFT, ipadx=5)
comboboxRowOfIO = tkinter.ttk.Combobox(frameSheet, state="readonly")
comboboxRowOfIO.pack(side=TC.LEFT, fill=TC.X, expand=True)

##frameChangeMotorStatus
frameChangeMotorStatus = tkinter.Frame(frameAutoDeal, relief=TC.RIDGE, borderwidth=2)
frameChangeMotorStatus.pack(fill=TC.X, expand=True)
motorLabel = tkinter.Label(frameChangeMotorStatus, text="电机", borderwidth=2)
motorLabel.pack(side=TC.LEFT, ipadx=5)
comboboxMotor = tkinter.ttk.Combobox(frameChangeMotorStatus, state="readonly")
comboboxMotor.pack(side=TC.LEFT, fill=TC.X, ipadx=45, expand=True)
switchLabel = tkinter.Label(frameChangeMotorStatus, text="限位", borderwidth=2)
switchLabel.pack(side=TC.LEFT, ipadx=5)
comboboxSwitch = tkinter.ttk.Combobox(frameChangeMotorStatus, state="readonly")
comboboxSwitch.pack(side=TC.LEFT, fill=TC.X, ipadx=45, expand=True)
comboboxSwitch['value']  = ['ON_A', 'ON_B', '取反']
switchButton = tkinter.Button(frameChangeMotorStatus, text="改变限位判定", command=on_change_switch)
switchButton.pack(side=TC.RIGHT, ipadx=20)

##frameChangeIOName
frameChangeIOName = tkinter.Frame(frameAutoDeal, relief=TC.RIDGE, borderwidth=2)
frameChangeIOName.pack(fill=TC.X, expand=True)
portLabel = tkinter.Label(frameChangeIOName, text="Port", borderwidth=2)
portLabel.pack(side=TC.LEFT, ipadx=5)
comboboxPort = tkinter.ttk.Combobox(frameChangeIOName, state="normal")
comboboxPort.pack(side=TC.LEFT, fill=TC.X, ipadx=45, expand=True)
newPortLabel = tkinter.Label(frameChangeIOName, text="", borderwidth=2)
newPortLabel.pack(side=TC.LEFT, ipadx=5)
varNewIOName = tkinter.StringVar()
entryNewIOName = tkinter.Entry(frameChangeIOName, bg='white', textvariable=varNewIOName)
entryNewIOName.pack(side=TC.LEFT, fill=TC.X, ipadx=45, expand=True)
changIONameButton = tkinter.Button(frameChangeIOName, text="改变端口标识", command=on_change_IOName)
changIONameButton.pack(side=TC.RIGHT, ipadx=20)
changIDButton = tkinter.Button(frameChangeIOName, text="改变端口ID", command=on_change_id)
changIDButton.pack(side=TC.RIGHT, ipadx=20)

##frameDeal
frameDeal = tkinter.Frame(frameAutoDeal, relief=TC.RIDGE, borderwidth=2)
frameDeal.pack(fill=TC.X, expand=1)
checkDataButton = tkinter.Button(frameDeal, text="检查数据赋值", command=on_check_data)
checkDataButton.pack(side=TC.RIGHT, ipadx=45)
checkDataCompareButton = tkinter.Button(frameDeal, text="检查数据比较", command=on_check_data_compare)
checkDataCompareButton.pack(side=TC.RIGHT, ipadx=45)
checkDataCalcButton = tkinter.Button(frameDeal, text="检查数据计算", command=on_check_data_calc)
checkDataCalcButton.pack(side=TC.RIGHT, ipadx=45)
checkEncoderButton = tkinter.Button(frameDeal, text='检查编码器', command=on_check_encoder)
checkEncoderButton.pack(side=TC.RIGHT, ipadx=45)
clearUnusedButton = tkinter.Button(frameDeal, text='清除无用动作', command=on_clear_unused_action)
clearUnusedButton.pack(side=TC.RIGHT, ipadx=45)
markUnusedButton = tkinter.Button(frameDeal, text='标识无用动作', command=on_mark_unused_action)
markUnusedButton.pack(side=TC.RIGHT, ipadx=45)
exportSupportButton = tkinter.Button(frameDeal, text='设备支持列表', command=on_export_DevicesList)
exportSupportButton.pack(side=TC.RIGHT, ipadx=45)

##frameAutoAdd
frameAutoAdd = tkinter.Frame(frameAutoCopy, relief=TC.RIDGE, borderwidth=2)
frameAutoAdd.pack(fill=TC.X, expand=True)
startActionLabel = tkinter.Label(frameAutoAdd, text="开始动作号", borderwidth=2)
startActionLabel.pack(side=TC.LEFT, ipadx=5)
varStartAction = tkinter.StringVar()
entryStartAction = tkinter.Entry(frameAutoAdd, bg='white', textvariable=varStartAction)
entryStartAction.pack(side=TC.LEFT, fill=TC.X, expand=True)
countOfActionLabel = tkinter.Label(frameAutoAdd, text="动作数量", borderwidth=2)
countOfActionLabel.pack(side=TC.LEFT, ipadx=5)
varCountOfAction = tkinter.StringVar()
entryCountOfAction = tkinter.Entry(frameAutoAdd, bg='white', textvariable=varCountOfAction)
entryCountOfAction.pack(side=TC.LEFT, fill=TC.X, expand=True)
labelXOffset = tkinter.Label(frameAutoAdd, text="X坐标增量", borderwidth=2)
labelXOffset.pack(side=TC.LEFT, ipadx=5)
varXOffset = tkinter.StringVar()
entryXOffset = tkinter.Entry(frameAutoAdd, bg='white', textvariable=varXOffset)
entryXOffset.pack(side=TC.LEFT, fill=TC.X, expand=True)
labelYOffset = tkinter.Label(frameAutoAdd, text="Y坐标增量", borderwidth=2)
labelYOffset.pack(side=TC.LEFT, ipadx=5)
varYOffset = tkinter.StringVar()
entryYOffset = tkinter.Entry(frameAutoAdd, bg='white', textvariable=varYOffset)
entryYOffset.pack(side=TC.LEFT, fill=TC.X, expand=True)
countOfCopyLabel = tkinter.Label(frameAutoAdd, text="复制数量", borderwidth=2)
countOfCopyLabel.pack(side=TC.LEFT, ipadx=5)
varCountOfCopy = tkinter.StringVar()
entryCountOfCopy = tkinter.Entry(frameAutoAdd, bg='white', textvariable=varCountOfCopy)
entryCountOfCopy.pack(side=TC.LEFT, fill=TC.X, expand=True)

##frameAutoAdd
frameAutoAddBtn = tkinter.Frame(frameAutoCopy, relief=TC.RIDGE, borderwidth=2)
frameAutoAddBtn.pack(fill=TC.X, expand=1)
selfCopyButton = tkinter.Button(frameAutoAddBtn, text="模组内自我复制", command=on_self_copy)
selfCopyButton.pack(side=TC.RIGHT, ipadx=45)
copyToButton = tkinter.Button(frameAutoAddBtn, text="Copy to新模组", command=on_copy_to_new_module)
copyToButton.pack(side=TC.RIGHT, ipadx=45)
copyToOtherXmlButton = tkinter.Button(frameAutoAddBtn, text="Copy to其他流程", command=on_copy_to_other_xml)
copyToOtherXmlButton.pack(side=TC.RIGHT, ipadx=45)
movePointXYButton = tkinter.Button(frameAutoAddBtn, text="模组内动作坐标移动", command=on_move_point_xy)
movePointXYButton.pack(side=TC.RIGHT, ipadx=45)

##frameUI
frameUI = tkinter.Frame(frameUIDeal, relief=TC.RIDGE, borderwidth=2)
frameUI.pack(fill=TC.X, expand=1)
varUILabel = tkinter.StringVar()
UILabel = tkinter.Entry(frameUI, bg='white', textvariable=varUILabel)
UILabel.pack(side=TC.LEFT, fill=TC.X, expand=1)
UIButton = tkinter.Button(frameUI, text="选择.ui文件夹", command=on_UI_select)
UIButton.pack(side=TC.LEFT, ipadx=20)
btnDealUI = tkinter.Button(frameUI, text="地址", command=on_deal_UI)
btnDealUI.pack(side=TC.RIGHT, ipadx=20)
btnDealPort = tkinter.Button(frameUI, text="端口", command=on_deal_UI_port)
btnDealPort.pack(side=TC.RIGHT, ipadx=20)

##frameSysform
frameSysform = tkinter.Frame(frameUIDeal, relief=TC.RIDGE, borderwidth=2)
frameSysform.pack(fill=TC.X, expand=1)
varSysform = tkinter.StringVar()
entrySysform = tkinter.Entry(frameSysform, bg='white', textvariable=varSysform)
entrySysform.pack(side=TC.LEFT, fill=TC.X, expand=1)
btnSysform = tkinter.Button(frameSysform, text="选择sysform_kh.ui文件", command=on_sysform_select)
btnSysform.pack(side=TC.LEFT, ipadx=20)
btnDealSysform = tkinter.Button(frameSysform, text="地址", command=on_deal_sysform)
btnDealSysform.pack(side=TC.RIGHT, ipadx=20)

frameText = tkinter.Frame(windows, relief=TC.RIDGE, borderwidth=2)
frameText.pack(fill=TC.BOTH, expand=1)
t = tkinter.Text(frameText, height=50)
t.pack(side=TC.LEFT, fill=TC.BOTH, expand=1)
scrollY = tkinter.Scrollbar(frameText)
scrollY.pack(side=TC.RIGHT, fill=TC.Y) # side是滚动条放置的位置，上下左右。fill是将滚动条沿着y轴填充
scrollY.config(command=t.yview) # 将文本框关联到滚动条上，滚动条滑动，文本框跟随滑动
t.config(yscrollcommand=scrollY.set) # 将滚动条关联到文本框

#加载配置
try:
    cfgFile = getCurrentPath() + os.path.sep + "config.cfg"
    config = {}
    with open(cfgFile) as fileObj:
        config = json.load(fileObj)

        varXmlLabel.set(config.get('xmlFile', ''))
        varExcelLabel.set(config.get('excelFile', ''))
        varOutputLabel.set(config.get('outputFile', ''))

        if "Module" in config.keys():
            comboboxModule.set(config["Module"])
        if "StartAction" in config.keys():
            varStartAction.set(config["StartAction"])
        if "CountOfAction" in config.keys():
            varCountOfAction.set(config["CountOfAction"])
        if "XOffset" in config.keys():
            varXOffset.set(config["XOffset"])
        if "YOffset" in config.keys():
            varYOffset.set(config["YOffset"])
        if "CountOfCopy" in config.keys():
            varCountOfCopy.set(config["CountOfCopy"])

        varUILabel.set(config.get('UI_Dir', ''))
        varSysform.set(config.get('Sysform_Dir', ''))

except Exception as Err:
    errStr = str(Err)
    # debugOnText(errStr)

reload_xml(varXmlLabel.get())
reload_excel(varExcelLabel.get())
windows.mainloop()

config["StartAction"] = varStartAction.get()
config["CountOfAction"] = varCountOfAction.get()
config["XOffset"] = varXOffset.get()
config["YOffset"] = varYOffset.get()
config["CountOfCopy"] = varCountOfCopy.get()

with open(cfgFile, "w") as fileObj:
    json.dump(config, fileObj, indent="\t")
