import xlrd

class ExcelException(Exception):
    pass

class MyExcel:
    def __init__(self, file) -> None:
        self.workbook = xlrd.open_workbook(filename=file)

    def get_portlist(self, excelSheetName, colOfChannel, colOfMark, colOfIO):
        try:
            sheet1 = self.workbook.sheet_by_name(excelSheetName)
    
            #先介绍一下merged_cells()用法，merged_cells返回的这四个参数的含义是：(row,row_range,col,col_range),
            #其中[row,row_range)包括row,不包括row_range,col也是一样，
            #即(1, 3, 4, 5)的含义是：第1到2行（不包括3）合并，(7, 8, 2, 5)的含义是：第2到4列合并。
            colOfChannel = int(colOfChannel)
            colOfMark = int(colOfMark)
            colOfIO = int(colOfIO)
            
            chMergedCells = []
            motorNameMergeCells = {}
            for mergedCell in sheet1.merged_cells:
                name = sheet1.cell_value(mergedCell[0], mergedCell[2])
                if mergedCell[2] == colOfChannel:#获取第G列
                    #print(name)
                    if name.find("通道")>0:
                        chMergedCells.append(mergedCell)
                elif mergedCell[2] == colOfMark:#标号所在列
                    if name.startswith("M"):#电机的端口
                        if name.find("-T") > 0:#跳过电机的M11-T1
                            pass
                        else:
                            motorNameMergeCells[name] = mergedCell

            portList={} 
            for chMergedCell in chMergedCells:
                # print("+"*50)
                # print(sheet1.cell_value(chMergedCell[0], chMergedCell[2]))#QZ-D5216-210(A)通道0
                channelID=sheet1.cell_value(chMergedCell[0], chMergedCell[2])[-1:]#QZ-D5216-210(A)合并的行才会算到QZ-D5216-210(A)的通道
                # print("-"*50)
                for i in range(chMergedCell[0], chMergedCell[1]):
                    if sheet1.cell(i, colOfMark).ctype == xlrd.biffh.XL_CELL_TEXT:
                        # print("%s:%s" % (sheet1.cell_value(i, colOfMark), sheet1.cell_value(i, colOfIO)))
                        portMap={}
                        portMap["PortIOName"]=sheet1.cell_value(i, colOfMark)
                        if portMap["PortIOName"].startswith("M"):#电机的端口
                            if portMap["PortIOName"].find("-T") > 0:#跳过电机的M11-T1
                                continue

                            if portMap["PortIOName"] in motorNameMergeCells and i==motorNameMergeCells[portMap["PortIOName"]][0]:
                                for j in range(motorNameMergeCells[portMap["PortIOName"]][0], motorNameMergeCells[portMap["PortIOName"]][1]):
                                    ioStr=sheet1.cell_value(j, colOfIO)

                                    if ioStr.find('CW') < 0: #not CW or CCW
                                        continue

                                    ioStr=ioStr[-1:]#CW2
                                    portMap["ChannelID"]=str(4*int(channelID)+int(ioStr))#一个通道带4个电机
                                    portMap["IONum"]="0"#电机不用端口属性
                                    portList[portMap["PortIOName"]]=portMap
                                    break
                        else:
                            portMap["ChannelID"]=channelID
                            ioStr=sheet1.cell_value(i, colOfIO)
                            ioStr=ioStr.replace("INPUT","")
                            ioStr=ioStr.replace("OUTPUT","")
                            portMap["IONum"]=ioStr
                            portList[portMap["PortIOName"]]=portMap
                # print("-"*50)
        except Exception as Err:
            if chMergedCells:
                sErrMsg = "{e}(行:{r},列:{c},内容:{content})".format(e=str(Err), r=i, c=chr(ord('A')+colOfMark), content=sheet1.cell_value(i, colOfMark))
            else:
                sErrMsg = str(Err)
            raise ExcelException(sErrMsg)
        else:      
            # print("*"*100)        
            # for k,v in portList.items():
                # print(k,v)
            return portList        