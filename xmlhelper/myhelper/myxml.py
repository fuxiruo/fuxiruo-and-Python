import logging
import xml.etree.ElementTree as ET

"""
注意：解析xml然后修改保存时节点的属性默认会被重新排序
可以修改ElementTree.py源码，_serialize_xml函数
只需要修改这一行代码，将
for k, v in sorted(items):
改成
for k, v in items: 
"""
myxml_logger = logging.getLogger('main.{}'.format(__name__))
myxml_logger.setLevel(logging.INFO)

class MyXml:
    def __init__(self, xmlFile):
        xmlFileText = open(xmlFile, encoding='gbk').read()
        self.root = ET.fromstring(xmlFileText)

    def iter_module(self):
        for moduleLists in self.root.iter('ModuleList'):
            for module in moduleLists:
                # myxml_logger.debug(module)
                yield module

    def iter_action(self, path):
        for runActions in self.root.iter('RunAction'):
            for action in runActions:
                yield action

    def find_action(self, start_node, objType):
        for action in start_node.findall('.//*[@ActionID]/[@ObjType="{}"]'.format(objType)):
            yield action

    def iter_port(self):
        for portLists in self.root.iter('PortList'):
            for port in portLists:
                yield port

    def get_module_name_id_list(self):
        name_id_List = []
        for module in self.iter_module():
            nameID = module.attrib['ModuleName'] + '|' + module.attrib['ModuleID']
            name_id_List.append(nameID)
        return name_id_List
    
    def get_port_id_list(self):
        motor_id_List = []
        port_id_List = []
        for port in self.iter_port():
            name_objID = port.attrib['PortIOName'] + '|' + port.attrib['PortCName'] + '|' + port.attrib['ObjectID']
            port_id_List.append(name_objID)

            if '2'==port.attrib['PortType']:
                name_objID = port.attrib['PortCName'] + '|' + port.attrib['ObjectID']
                motor_id_List.append(name_objID)

        return port_id_List,motor_id_List

    def get_portlist(self, bIdAsKey=False):
        portList={}

        for port in self.iter_port():
            if port.attrib["PortType"]>"1":
                portType="MOTOR"
            elif port.attrib["PortType"]=="0":
                portType="OUTPUT"
            else:
                portType="INPUT"
            portMap={}
            portMap["ID"] = int(port.attrib["ObjectID"])
            portMap["PortIOName"]=port.attrib["PortIOName"].strip().strip('\n\r')
            portMap["PortType"]=portType
            portMap["ChannelID"]=port.attrib["ChannelID"]
            portMap["IONum"]=port.attrib["IONum"]

            if bIdAsKey:
                portList[portMap["ID"]]=portMap
            else:
                portList[portMap["PortIOName"]]=portMap
            # print("%s:%s\t%s:%s" % (port.attrib["PortIOName"], portType, port.attrib["ChannelID"], port.attrib["IONum"]))
            
        return portList

    def find_inconnection_action(self, moduleIDToChange=None, startAction=None):
        toSearchAction = []
        allSearchAction = {}

        for module in self.iter_module():
            if moduleIDToChange != None and moduleIDToChange != module.attrib['ModuleID']:
                continue 

            myxml_logger.debug("*"*45 + module.tag + "*"*45)
            hadSearchAction = set() 
            if startAction == None:
                FirstAction = module.attrib['FirstAction']
            else:
                FirstAction = startAction
            toSearchAction.append(FirstAction)
            while len(toSearchAction) > 0:
                actionToFind = toSearchAction.pop()

                if actionToFind in hadSearchAction:
                    continue

                hadSearchAction.add(actionToFind)
                action = module.find('.//*[@ActionID="{}"]'.format(actionToFind))
                if not action is None:
                    myxml_logger.debug(action.attrib['ActionName'])
                    DefaultAction = action.attrib['DefaultAction']
                    IsTrue_NextAction = action.attrib['IsTrue_NextAction']
                    IsFalse_NextActiton = action.attrib['IsFalse_NextActiton']

                    if (IsFalse_NextActiton != '-1') and (not IsFalse_NextActiton in hadSearchAction):
                        toSearchAction.append(IsFalse_NextActiton)
                    if (IsTrue_NextAction != '-1') and (not IsTrue_NextAction in hadSearchAction):
                        toSearchAction.append(IsTrue_NextAction)
                    if (DefaultAction != '-1') and (not DefaultAction in hadSearchAction):
                        toSearchAction.append(DefaultAction)
        
                allSearchAction[module.attrib['ModuleID']] = hadSearchAction #添加的只是引用，所以每个模组需要重新hadSearchAction = set() 

            if moduleIDToChange != None:
                break

        return allSearchAction

    def find_start_unused_actionID(self, moduleID):
        """找到模组未开始使用的一个ActionID"""
        unusedActionID = ""

        for module in self.iter_module():
            if moduleID != module.attrib['ModuleID']:
                continue 

            myxml_logger.debug("*"*45 + module.tag + "*"*45)

            for runActions in module.iter('RunAction'):
                for action in runActions:
                    unusedActionID = action.attrib['ActionID']
            break
        
        nextNewAcitionID = int(unusedActionID)+1
        myxml_logger.info("find_start_unused_actionID:"+str(nextNewAcitionID))
        return nextNewAcitionID

    @staticmethod
    def get_new_xml_replace_by_iter_line(origFile, newFile, funcReplace=None, moduleIDToChange=None):
        bFindModuleStart = False
        bFindModuleEnd = False
        bNeedChange = True

        with open(newFile, 'w') as newFileObj:
            with open(origFile,encoding='gbk') as fileObj:
                for line in fileObj:
                    newLine = line

                    if bNeedChange:
                        if not moduleIDToChange: #替换所有模组
                            bFindModuleStart = True
                            bFindModuleEnd = False
                        else:#替换指定模组
                            if not bFindModuleStart:
                                indexOfModuleStart = newLine.find('" ModuleID="{}"'.format(moduleIDToChange))
                                if indexOfModuleStart > 0:
                                    bFindModuleStart = True
                                    myxml_logger.info('module start find:' + newLine)
                            elif bFindModuleStart and not bFindModuleEnd:
                                indexOfModuleStart = newLine.find('ModuleID="{}"'.format(moduleIDToChange))  
                                if indexOfModuleStart < 0:  
                                    bFindModuleEnd = True  
                                    bNeedChange = False 
                                    myxml_logger.info('module end find:' + newLine)  

                        # 替换
                        if bFindModuleStart and not bFindModuleEnd:
                            if funcReplace:
                                newLine = funcReplace(newLine) 
                                if line != newLine:
                                    myxml_logger.debug(line + '=>' + newLine)  
                                    myxml_logger.debug("-"*80)

                    newFileObj.write(newLine)

    @staticmethod
    def get_old_action_id_to_new(xmlFile, toCopyAction, moduleID, newActionNo):
        bFindModuleStart = False
        bFindModuleEnd = False
        needCopyLines = []
        oldNewActionIDMap = {}

        with open(xmlFile,encoding='gbk') as fileObj:
            for line in fileObj:
                newLine = line

                if not bFindModuleStart:
                    indexOfModuleStart = newLine.find('" ModuleID="{}"'.format(moduleID))
                    if indexOfModuleStart > 0:
                        bFindModuleStart = True
                elif bFindModuleStart and not bFindModuleEnd:
                    indexOfModuleStart = newLine.find('ModuleID="{}"'.format(moduleID))  
                    if indexOfModuleStart < 0:  
                        bFindModuleEnd = True   
                        break

                if len(toCopyAction) == 0:
                    break

                if bFindModuleStart and not bFindModuleEnd:
                    for actionToFind in toCopyAction:
                        indexOfAction = newLine.find('ActionID="{}"'.format(actionToFind))
                        if indexOfAction > 0:
                            myxml_logger.debug('action find:' + newLine)
                            oldNewActionIDMap[actionToFind] = newActionNo
                            needCopyLines.append(newLine)
                            toCopyAction.remove(actionToFind)
                            newActionNo = newActionNo + 1
                            break   

        return  oldNewActionIDMap,needCopyLines               