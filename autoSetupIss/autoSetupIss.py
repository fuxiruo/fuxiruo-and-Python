import os
from re import template

"""
将antoSetup.py和setupTemplate.iss置于需要生成发布包的运行目录下，运行antoSetup.py即可生成所需要的setup.iss
"""

DIR_TEMPALTE = r'Source: ".\{DIR}\*"; DestDir: "{{app}}\{DIR}\"; Flags: ignoreversion recursesubdirs createallsubdirs'
FILE_TEMPLATE = r'Source: ".\{FILE}"; DestDir: "{{app}}"; Flags: ignoreversion'

def getCurrentPath():
    current_path = os.path.dirname(__file__)
    return current_path
    
def GetDirsAndFiles():
    dirs = []
    files = []
    with os.scandir(getCurrentPath()) as it:
        for entry in it:
            if entry.is_file():
                if not entry.name.endswith(".py") and not entry.name.endswith(".iss"):
                    print('file:' + entry.name)
                    files.append(entry.name)
            elif entry.is_dir():
                print('dri:' + entry.name)
                dirs.append(entry.name)

    return dirs,files

def GetFilesLines():
    lines = []
    linesDir = []
    linesFile = []

    dirs,files = GetDirsAndFiles()

    for dir in dirs:
        sDir = DIR_TEMPALTE.format(DIR=dir)
        print(sDir)
        linesDir.append(sDir)

    fileExts = set()
    for file in files:
        sFile = ""
        root,ext = os.path.splitext(file)
        if ext:
            if ext not in fileExts:
                fileExts.add(ext)
                sFile = FILE_TEMPLATE.format(FILE='*' + ext)
        else:
            sFile = FILE_TEMPLATE.format(FILE=file) 
        
        if sFile:
            print(sFile)
            linesFile.append(sFile)

    # linesFile.sort()
    lines.extend(linesDir)
    lines.extend(linesFile)

    return lines

try:
    newXmlFile = getCurrentPath() + '/setup.iss'
    with open(newXmlFile, 'w') as newFileObj:
        with open(getCurrentPath() + '/setupTemplate.iss', encoding='GBK') as f:
            print(f)
            for line in f:
                newFileObj.write(line)

                if(line.startswith("[Files]")):
                    for fileLine in GetFilesLines():
                        newFileObj.write(fileLine + '\n')
                    
    print(newXmlFile + " Done!")
except Exception as Err:
    print(str(Err))

print("press enter to exit")
input()