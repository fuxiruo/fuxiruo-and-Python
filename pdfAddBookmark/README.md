# 利用PyPDF2给pdf文件加书签

### 测试环境
Python3.8.4 PyPDF2-1.26.0 

没修改pdf.py源码前会报错：
***
add title:第1章Delphi概述,page:21
Traceback (most recent call last):
  File "f:/ko/Python/fuxiruo-and-Python/pdfAddBookmark/pdfAddBookmark.py", line 122, in <module>
    addBookmark(pdf_file, bookmark_file, 20)
  File "f:/ko/Python/fuxiruo-and-Python/pdfAddBookmark/pdfAddBookmark.py", line 92, in addBookmark
    new_bookmark = writer.addBookmark(title, page, parent)
  File "E:\Python\Python38\lib\site-packages\PyPDF2\pdf.py", line 721, in addBookmark
    outlineRef = self.getOutlineRoot()
  File "E:\Python\Python38\lib\site-packages\PyPDF2\pdf.py", line 605, in getOutlineRoot
    idnum = self._objects.index(outline) + 1
ValueError: {'/Type': '/Outlines', '/First': IndirectObject(7276, 0), '/Last': IndirectObject(7279, 0), '/Count': 3} is not in list
***

需要将pdf.py文件中的getOutlineRoot函数修改为：
```
def getOutlineRoot(self):
        if '/Outlines' in self._root_object:
            outline = self._root_object['/Outlines']
            if outline in self._objects:
                print('getOutlineRoot1')
                idnum = self._objects.index(outline) + 1
                outlineRef = IndirectObject(idnum, 0, self)
                assert outlineRef.getObject() == outline
            else:
                print('getOutlineRoot2')
                outline = TreeObject()
                outline.update({ })
                outlineRef = self._addObject(outline)
                self._root_object[NameObject('/Outlines')] = outlineRef
        else:
            print('getOutlineRoot3')
            outline = TreeObject()
            outline.update({ })
            outlineRef = self._addObject(outline)
            self._root_object[NameObject('/Outlines')] = outlineRef

        return outline
```

***

书签的格式如下：
```
第 1 章 Delphi 概述············································································································· 1 
1.1 Delphi 介绍··············································································································· 1 
1.2 Delphi 7 的主要特性································································································· 2 
```

代码自动提取书签为：
```
add title:第1章Delphi概述,page:21
add title:1.1Delphi介绍,page:21
add title:1.2Delphi7的主要特性,page:22
```

需要制作一个包含书签的txt文档，例如book.txt，和还没有加书签的pdf文件，例如Delphi7 程序设计与开发技术大全.pdf。addBookmark(pdf_file, bookmark_file, 20)中的参数20，表示book.txt的页码和pdf文件对应的页码的偏移：
```
if __name__ == "__main__":
    bookmark_file = getCurrentPath() + os.path.sep +  r'book.txt'
    pdf_file = getCurrentPath() + os.path.sep +  r'Delphi7 程序设计与开发技术大全.pdf'

    addBookmark(pdf_file, bookmark_file, 20)
```