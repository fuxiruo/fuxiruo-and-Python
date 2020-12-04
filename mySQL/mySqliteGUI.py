import tkinter
import tkinter.ttk
import tkinter.filedialog
import tkinter.messagebox
import tkinter.constants as tkc
import logging
import os
import json
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
    global comboboxTables

    if "DbDir" in config.keys():
        DbDir = config["DbDir"]
    else:
        DbDir = getCurrentPath()

    file = tkinter.filedialog.askopenfilename(title="选择数据库文件", filetypes=[("db files", "*.db")], initialdir=DbDir)#返回文件名
    varDBFile.set(file)

    if len(file) > 0:
        config["DbDir"] = os.path.dirname(file)

        mySqlite.open(varDBFile.get())

        comboboxTables['value'] = mySqlite.get_tables()
        # comboboxTables.current(0)

def OnOutputSelect():
    global varOutput

    if "OutputDir" in config.keys():
        OutputDir = config["OutputDir"]
    else:
        OutputDir = getCurrentPath()

    file = tkinter.filedialog.askdirectory(title="选择数据库文件", initialdir=OutputDir)#返回文件夹
    if len(file)>0:
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

def OnDBExport():
    global comboboxTables

    if not comboboxTables.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择表!')
        return
    
    cmd = '.dump {}'.format(comboboxTables.get())
    debugOnText(cmd)
    result = excute_sqlite(cmd)
    debugOnText(result)

    outPutFile = varOutput.get() + os.path.sep + comboboxTables.get() + '.sql'
    with open(outPutFile, 'w', newline='', encoding='utf-8') as f:
        f.write(result) 

def OnDBImport():
    global varInput

    if not varInput.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择文件!')
        return
    
    cmd = '.read {}'.format(varInput.get())
    debugOnText(cmd)
    result = excute_sqlite(cmd)
    debugOnText(result)

def OnDBDel():
    global comboboxTables

    if not comboboxTables.get():
        tkinter.messagebox.showwarning(title='警告', message='请先选择表!')
        return

    mySqlite.del_table(comboboxTables.get())
    debugOnText('del ' + comboboxTables.get() + ' ok')
    comboboxTables['value'] = mySqlite.get_tables()

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
varOutput.set(getCurrentPath())
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

# frameDBInfo
frameDBInfo = tkinter.Frame(windows, relief=tkc.RIDGE, borderwidth=2)
frameDBInfo.pack(fill=tkc.X, expand=True)
labelTables = tkinter.Label(frameDBInfo, text="表", borderwidth=2)
labelTables.pack(side=tkc.LEFT, ipadx=5)
comboboxTables = tkinter.ttk.Combobox(frameDBInfo, state="readonly")
comboboxTables.pack(side=tkc.LEFT, fill=tkc.X, expand=True)

# frameText
frameText = tkinter.Frame(windows, relief=tkc.RIDGE, borderwidth=2)
frameText.pack(fill=tkc.BOTH, expand=1)
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
except Exception as Err:
    errStr = str(Err)
    # debugOnText(errStr)

windows.mainloop()

with open(cfgFile, "w") as fileObj:
    json.dump(config, fileObj, indent="\t")
