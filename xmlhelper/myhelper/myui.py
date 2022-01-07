import logging
import os
import re
import xml.etree.ElementTree as ET
from collections import namedtuple

myui_logger = logging.getLogger('main.{}'.format(__name__))
myui_logger.setLevel(logging.INFO)

SensorLevel = namedtuple('SensorLevel', 'sensor, level')
ItemLevel = namedtuple('ItemLevel', 'item, level')

class MyUI:
    def __init__(self, uiFile):
        self._file = uiFile
        xmlFileText = open(uiFile, encoding='utf-8').read()
        self.root = ET.fromstring(xmlFileText)

    def get_addrlist(self):
        addrList={}
        for widget in self.root.iter('widget'):
            # print(widget.attrib['class'])
            if widget.attrib['class'] == 'qhStepInput' \
                or widget.attrib['class'] == 'qhINTInput'  \
                or widget.attrib['class'] == 'qhSimpleSelect':
                propertMap = {}
                for propertys in widget.iter('property'):
                    if propertys.attrib['name'] == 'LabelComponentName':
                        propertMap['LabelComponentName'] = propertys.find('string').text
                        label = self.root.find(".//*[@name='{}']".format(propertMap['LabelComponentName']))

                        if label:
                            # print(propertMap['LabelComponentName'], label.attrib)
                            text_label = label.find(".//*[@name='text']/string")
                            # print(text_label.attrib)
                            # print(text_label.text)
                            propertMap['Titlename'] = text_label.text
                            # print(propertMap['Titlename'])
                        else:
                            propertMap['Titlename'] = '!'*10 + '缺失' + '!'*10
                    elif propertys.attrib['name'] == 'valueMode':
                        propertMap['valueMode'] = propertys.find('enum').text
                        # print(propertMap['valueMode'])
                    elif propertys.attrib['name'] == 'RamAddress':
                        propertMap['RamAddr'] = propertys.find('UInt').text
                        # print(propertMap['RamAddr'])

                addrList['{}-{}'.format(os.path.basename(self._file).split('.')[0], widget.attrib['name'])] = propertMap

        return addrList

    def get_addrlist_from_sysform_ui(self):
        addrList={}
        for widget in self.root.iter('widget'):
            if widget.attrib['class'] == 'ConfigLineEdit' \
                or widget.attrib['class'] == 'ConfigDeviceOpenOrClose'  \
                or widget.attrib['class'] == 'ConfigCheckbox':
                propertMap = {}
                for propertys in widget.iter('property'):
                    if propertys.attrib['name'] == 'Titlename' \
                        or propertys.attrib['name'] == 'TitleName' \
                        or propertys.attrib['name'] == 'Tisinfo':
                        propertMap['Titlename'] = propertys.find('string').text
                        # print(propertMap['Titlename'])
                    elif propertys.attrib['name'] == 'valueMode':
                        propertMap['valueMode'] = propertys.find('enum').text
                        # print(propertMap['valueMode'])
                    elif propertys.attrib['name'] == 'RamAddr':
                        propertMap['RamAddr'] = propertys.find('string').text
                        # print(propertMap['RamAddr'])

                addrList[widget.attrib['name']] = propertMap

        return addrList

    def get_portlist(self):
        portList = []

        item_level_list = []
        now_level = 0
        item_level_list.append(ItemLevel(self.root, now_level))
        sensor_level_list = []
        latest_layout = None
        latest_layout_level = 0
        while len(item_level_list) > 0:
            now_item_level = item_level_list.pop()
            now_item = now_item_level.item
            now_level = now_item_level.level

            if len(list(now_item)) > 0:
                bfind_qhsensor = False
                for item in now_item:
                    if item.tag == 'widget':
                        if item.attrib['class'] == 'qhSensor':
                            # print('*'*50)
                            bfind_qhsensor = True
                            sensor_level_list.append(SensorLevel(item, now_level))
                            # print('add sensor:', now_level, item.attrib['name'])

                            sensor_id = ''
                            sensor_name = ''
                            item_id = item.find('.//*[@name="ID"]/UInt')
                            if item_id is not None:
                                # print('sensor id:', item_id.attrib,  item_id.text)
                                sensor_id = item_id.text

                            # 按照qhSensor和对应QLabel有布局在一起的话，会有一个layout在qhSensor的level-2
                            if latest_layout is not None:
                                # print('sensor layout:', latest_layout_level, latest_layout.attrib['name'])
                                if now_level-2 == latest_layout_level:
                                    #找QLabel
                                    sensor_label = latest_layout.find('.//*[@class="QLabel"]/*[@name="text"]/string')
                                    # print('sensor label:', sensor_label.text)
                                    if sensor_label is not None:
                                        sensor_name = sensor_label.text
                                        target_name_include = re.split(r'([a-zA-Z0-9-]+)', sensor_name)
                                        if len(target_name_include) > 1:
                                            sensor_name = target_name_include[1]
                                latest_layout = None
                                latest_layout_level = 0

                            temp_map = {}
                            temp_map['ID'] = int(sensor_id)
                            temp_map['Name'] = sensor_name
                            portList.append(temp_map)
                            break
                        elif item.attrib['class'] == 'qhDoubleOutput':
                            temp_id = ''
                            temp_name = ''
                            item_id = item.find('.//*[@name="ID"]/UInt')
                            if item_id is not None:
                                # print('sensor id:', item_id.attrib,  item_id.text)
                                temp_id = item_id.text
                            item_id = item.find('.//*[@name="ButtonAText"]/string')
                            if item_id is not None:
                                # print('sensor id:', item_id.attrib,  item_id.text)
                                temp_name = item_id.text
                                target_name_include = re.split(r'([a-zA-Z0-9-]+)', temp_name)
                                if len(target_name_include) > 1:
                                    temp_name = target_name_include[1]
                            temp_map = {}
                            temp_map['ID'] = int(temp_id)
                            temp_map['Name'] = temp_name.split(' ')[0]
                            portList.append(temp_map)
                    elif item.tag == 'layout':
                        latest_layout = item
                        latest_layout_level = now_level

                if not bfind_qhsensor:
                    now_level = now_level + 1
                    for item in now_item:
                        # print('add:', now_level, item.tag, item.attrib)
                        item_level_list.append(ItemLevel(item, now_level))

        return portList

    @staticmethod
    def get_ui_files(path):
        files = []

        with os.scandir(path) as it:
            for dir_or_file in it:
                sub_dirs = [dir_or_file]
                while len(sub_dirs) > 0:
                    entry = sub_dirs.pop()
                    try:
                        if entry.is_symlink():
                            myui_logger.info('skip symlink:' + entry.path)
                            continue
                        elif entry.is_file()  and entry.name.endswith('.ui'):
                            files.append(entry.path)
                        elif entry.is_dir():
                            with os.scandir(entry.path) as sub_dir_it:
                                sub_dirs[0:0] = sub_dir_it
                    except:
                        myui_logger.exception(entry.path)
                        continue

        return files
