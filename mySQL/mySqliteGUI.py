import tkinter
import tkinter.ttk
import tkinter.filedialog
import tkinter.messagebox
import tkinter.constants as tkc
import logging
import os
import json
import configparser
from datetime import datetime
from mysqlite import MySqlite 

LOG_FORMAT = '[%(asctime)s][%(levelname)5s][%(module)s:%(funcName)s][%(threadName)10s:%(thread)5d]->%(message)s'

logger = logging.getLogger(__name__)
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

mySqlite = MySqlite()

def OnDBFileSelect():
    global varDBFile
    global varTablesSelect

    if "DbDir" in config.keys():
        DbDir = config["DbDir"]
    else:
        DbDir = getCurrentPath()

    file = tkinter.filedialog.askopenfilename(title="选择数据库文件", filetypes=[("db files", "*.db")], initialdir=DbDir)#返回文件名
    varDBFile.set(file)

    if len(file) > 0:
        config["DbDir"] = os.path.dirname(file)

        mySqlite.open(varDBFile.get())

        varTablesSelect.set(mySqlite.get_tables())

def OnOutputSelect():
    global varOutput

    if "OutputDir" in config.keys():
        OutputDir = config["OutputDir"]
    else:
        OutputDir = getCurrentPath()

    file = tkinter.filedialog.askdirectory(title="选择输出文件夹", initialdir=OutputDir)#返回文件夹
    if len(file)>0:
        config["OutputDir"] = file

        varOutput.set(file)

def OnInputSelect():
    global varInput

    if "InputDir" in config.keys():
        InputDir = config["InputDir"]
    else:
        InputDir = getCurrentPath()

    file = tkinter.filedialog.askopenfilename(title="选择数据库文件", filetypes=[("sql files", "*.sql")], initialdir=InputDir)

    if len(file)>0:
        config["InputDir"] = os.path.dirname(file)

        varInput.set(file)

def OnParamSelect():
    global varParamInput

    if "ParamDir" in config.keys():
        InputDir = config["ParamDir"]
    else:
        InputDir = getCurrentPath()

    file = tkinter.filedialog.askopenfilename(title="选择数据库文件", filetypes=[("INI files", "*.ini")], initialdir=InputDir)

    if len(file)>0:
        config["ParamDir"] = os.path.dirname(file)

        varParamInput.set(file)

def OnDBExport():
    global listTables

    if len(listTables.curselection()) == 0:
        tkinter.messagebox.showwarning(title='警告', message='请先选择表!')
        return
    
    for index in listTables.curselection():
        tableGet = listTables.get(index)

        cmd = '.dump {}'.format(tableGet)
        debugOnText(cmd)
        result = excute_sqlite(cmd)
        debugOnText(result)

        outPutFile = varOutput.get() + os.path.sep + tableGet + '.sql'
        with open(outPutFile, 'w', newline='', encoding='utf-8') as f:
            f.write(result) 

def OnDBExportData():
    global comboboxTables

    if not mySqlite.is_open():
        tkinter.messagebox.showwarning(title='警告', message='请先打开数据库!')
        return

    if len(listTables.curselection()) == 0:
        tkinter.messagebox.showwarning(title='警告', message='请先选择表!')
        return
    
    for index in listTables.curselection():
        tableGet = listTables.get(index)
    
        cmd = 'select * from {}'.format(tableGet)
        debugOnText(cmd)
        rows = mySqlite._execute(cmd)

        sOuput = "INSERT INTO `{}` {} VALUES {};"

        outPutFile = varOutput.get() + os.path.sep + tableGet + '.sql'
        with open(outPutFile, 'w', newline='', encoding='utf-8') as f:
            f.write('BEGIN TRANSACTION;\n')
            for r in rows:
                # 第一列认为是自增ID，忽略
                sRow = sOuput.format(tableGet, str(tuple(r.keys()[1:])), str(tuple(r)[1:]))
                sRow = sRow.replace('None', 'NULL')
                debugOnText(sRow)
                f.write(sRow) 
                f.write("\n")
            f.write('COMMIT;')

def OnDBImport():
    global varInput

    if not varInput.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择文件!')
        return
    
    cmd = '.read {}'.format(varInput.get())
    debugOnText(cmd)
    result = excute_sqlite(cmd)
    debugOnText(result)

def OnParamImport():
    global varParamInput

    if not mySqlite.is_open():
        tkinter.messagebox.showwarning(title='警告', message='请先打开数据库!')
        return

    if not varParamInput.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择文件!')
        return

    try:
        config = configparser.ConfigParser()
        config.read(varParamInput.get(), encoding='utf-8')

        paramDirName = os.path.splitext(os.path.basename(varParamInput.get()))[0]
        debugOnText('begin import param ' + paramDirName)
        mySqlite._execute('BEGIN TRANSACTION')
        mySqlite._execute("delete from 'ParameterDirectory' where Name='{}'".format(paramDirName))
        mySqlite._execute("delete from 'ParameterDetail' where Name='{}'".format(paramDirName))
        mySqlite._execute("INSERT INTO `ParameterDirectory` (Name,Context,LastUpdate,Operator,IsUse) VALUES ('{NAME}','{NAME}','{DATE_TIME}','Administrator',1);".format(NAME=paramDirName, DATE_TIME=datetime.now().strftime(r'%Y/%m/%d %H:%M:%S')))
        for section in config.sections():
            ramType = config[section]['RamType']
            # print(type(ramType))
            ramAddr = config[section]['RamAddr']
            valueByte = 0
            valueInt = 0
            if "1"==ramType:
                valueByte = config[section]['Value']
            elif "2"==ramType:
                valueInt = config[section]['Value']
            userLabel = config[section]['Name']
            mySqlite._execute("INSERT INTO `ParameterDetail` (Name,WorkUI,ObjectName,UserLabel,RamType,RamAddr,Value_Byt,Value_INT,Value_TXT,Value_Flo,LastUpdate,Operator,Res1,IsUse) VALUES ('{NAME}','','','{USER_LABEL}',{RAM_TYPE},{RAM_ADDR},{VALUE_BYTE},{VALUE_INT},'',0.0,'{DATE_TIME}','Administrator',NULL,1);".format(NAME=paramDirName, USER_LABEL=userLabel, RAM_TYPE=ramType, RAM_ADDR=ramAddr, VALUE_BYTE=valueByte, VALUE_INT=valueInt, DATE_TIME=datetime.now().strftime(r'%Y/%m/%d %H:%M:%S')))

        mySqlite._execute('COMMIT')
        debugOnText('end')
    except Exception as Err:
        debugOnText(str(Err))
        tkinter.messagebox.showerror(title='导入失败', message=str(Err))
        raise

def OnDBDel():
    global listTables

    if len(listTables.curselection()) == 0:
        tkinter.messagebox.showwarning(title='警告', message='请先选择表!')
        return

    for index in listTables.curselection():
        tableGet = listTables.get(index)
        mySqlite.del_table(tableGet)
        debugOnText('del ' + tableGet + ' ok')

def getCurrentPath():
    current_path = os.path.dirname(__file__)
    return current_path

def excute_sqlite(cmd):
    sqlite_exe = getCurrentPath() + os.path.sep + 'sqlite3.exe'
    if not os.path.exists(sqlite_exe):
        tkinter.messagebox.showwarning(title='警告', message='找不到sqlite3.exe!')
        return

    final_cmd = sqlite_exe + " " + varDBFile.get() + ' "' + cmd + '"'
    logger.info(final_cmd)
    f = os.popen(final_cmd, mode='r', buffering=-1) 
    tempstream = f._stream
    result = tempstream.buffer.read().decode(encoding='utf-8')
    f.close()
    return result

def debugOnText(strLog):
    global textDebug
    
    log = "[" + datetime.now().isoformat(timespec='milliseconds') + "]"
    log += strLog + "\n"
    textDebug.insert('end', log)

#GUI      
logger.debug('hello world') 
windows = tkinter.Tk()
windows.geometry('800x600')
windows.title('sqlite小工具')

# frameDbFile
frameDbFile = tkinter.Frame(windows, relief=tkc.RIDGE, borderwidth=2)
frameDbFile.pack(fill=tkc.X, expand=1)
varDBFile = tkinter.StringVar()
entryDBFile = tkinter.Entry(frameDbFile, bg='white', textvariable=varDBFile)
entryDBFile.pack(side=tkc.LEFT, fill=tkc.X, expand=1)
buttonDBFile = tkinter.Button(frameDbFile, text="选择.db数据库", command=OnDBFileSelect)
buttonDBFile.pack(side=tkc.LEFT, ipadx=20)
buttonDBExportData = tkinter.Button(frameDbFile, text="导出表数据", command=OnDBExportData)
buttonDBExportData.pack(side=tkc.RIGHT, ipadx=20)
buttonDBExport = tkinter.Button(frameDbFile, text="导出表", command=OnDBExport)
buttonDBExport.pack(side=tkc.RIGHT, ipadx=20)
buttonDBImport = tkinter.Button(frameDbFile, text="导入表", command=OnDBImport)
buttonDBImport.pack(side=tkc.RIGHT, ipadx=20)
buttonDBDel = tkinter.Button(frameDbFile, text="清除表", command=OnDBDel)
buttonDBDel.pack(side=tkc.RIGHT, ipadx=20)

#frameOutput
frameOutput = tkinter.Frame(windows, relief=tkc.RIDGE, borderwidth=2)
frameOutput.pack(fill=tkc.X, expand=1)
varOutput = tkinter.StringVar()
entryOutput = tkinter.Entry(frameOutput, bg='white', textvariable=varOutput)
entryOutput.pack(side=tkc.LEFT, fill=tkc.X, expand=1)
buttonOutputSelect = tkinter.Button(frameOutput, text="选择输出", command=OnOutputSelect)
buttonOutputSelect.pack(side=tkc.LEFT, ipadx=20)

#frameIntput
frameIntput = tkinter.Frame(windows, relief=tkc.RIDGE, borderwidth=2)
frameIntput.pack(fill=tkc.X, expand=1)
varInput = tkinter.StringVar()
entryInput = tkinter.Entry(frameIntput, bg='white', textvariable=varInput)
entryInput.pack(side=tkc.LEFT, fill=tkc.X, expand=1)
buttonInputSelect = tkinter.Button(frameIntput, text="选择输入", command=OnInputSelect)
buttonInputSelect.pack(side=tkc.LEFT, ipadx=20)

#frameParam
frameParam = tkinter.Frame(windows, relief=tkc.RIDGE, borderwidth=2)
frameParam.pack(fill=tkc.X, expand=1)
varParamInput = tkinter.StringVar()
entryParamInput = tkinter.Entry(frameParam, bg='white', textvariable=varParamInput)
entryParamInput.pack(side=tkc.LEFT, fill=tkc.X, expand=1)
buttonParamSelect = tkinter.Button(frameParam, text="选择参数文件", command=OnParamSelect)
buttonParamSelect.pack(side=tkc.LEFT, ipadx=20)
buttonParamImport = tkinter.Button(frameParam, text="导入", command=OnParamImport)
buttonParamImport.pack(side=tkc.LEFT, ipadx=20)

# frameDBInfo
# frameDBInfo = tkinter.Frame(windows, relief=tkc.RIDGE, borderwidth=2)
# frameDBInfo.pack(fill=tkc.X, expand=True)
# labelTables = tkinter.Label(frameDBInfo, text="表", borderwidth=2)
# labelTables.pack(side=tkc.LEFT, ipadx=5)
# comboboxTables = tkinter.ttk.Combobox(frameDBInfo, state="readonly")
# comboboxTables.pack(side=tkc.LEFT, fill=tkc.X, expand=True)

# frameText
frameText = tkinter.Frame(windows, relief=tkc.RIDGE, borderwidth=2)
frameText.pack(fill=tkc.BOTH, expand=1)
# frameText #listTables 
varTablesSelect = tkinter.StringVar()
listTables = tkinter.Listbox(frameText, listvariable=varTablesSelect, selectmode='multiple')
listTables.pack(side=tkc.LEFT, fill=tkc.Y, expand=False)
scrollList = tkinter.Scrollbar(frameText)
scrollList.pack(side=tkc.LEFT, fill=tkc.Y) # side是滚动条放置的位置，上下左右。fill是将滚动条沿着y轴填充
scrollList.config(command=listTables.yview) # 将文本框关联到滚动条上，滚动条滑动，文本框跟随滑动
listTables.config(yscrollcommand=scrollList.set) # 将滚动条关联到文本框
# frameText #textDebug
textDebug = tkinter.Text(frameText, height=50)
textDebug.pack(side=tkc.LEFT, fill=tkc.BOTH, expand=1)
scrollY = tkinter.Scrollbar(frameText)
scrollY.pack(side=tkc.RIGHT, fill=tkc.Y) # side是滚动条放置的位置，上下左右。fill是将滚动条沿着y轴填充
scrollY.config(command=textDebug.yview) # 将文本框关联到滚动条上，滚动条滑动，文本框跟随滑动
textDebug.config(yscrollcommand=scrollY.set) # 将滚动条关联到文本框

#加载配置
try:
    cfgFile = getCurrentPath() + os.path.sep + "config.cfg"
    config = {}
    with open(cfgFile) as fileObj:
        config = json.load(fileObj)

        if 'OutputDir' in config:
            varOutput.set(config['OutputDir'])
        else:
            varOutput.set(getCurrentPath())
except Exception as Err:
    errStr = str(Err)
    # debugOnText(errStr)

windows.mainloop()

with open(cfgFile, "w") as fileObj:
    json.dump(config, fileObj, indent="\t")
