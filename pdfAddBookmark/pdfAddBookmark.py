import re
import os
from PyPDF2 import PdfFileReader, PdfFileWriter

def _parse_bookmark(lines):
    titles = []
    levels = []
    pages = []

    for line in lines:
        # 正则移除空格和.，如hah     afo..................o2->hahafoo2
        line = re.sub(r'\s+', '', line)
        line = re.sub(r'\.\.+', '', line)
        line = re.sub(r'\·\·+', '', line)

        # 标签格式22.1.4第一节…… 4，正则获取22.1.4
        m = re.match(r'\d+(\.\d+)*', line)
        if m:
            level = m.group().count('.') # .来确认书签的级别 
        else: # 第 1 章 Delphi 概述,没有x.x.x的形式
            level = 0
        levels.append(level)    
        
        # m = re.match(r'.*[^\d](\d+)$', line) # 匹配最后的页码   
        m = re.search(r'(\d+)$', line) # 匹配最后的页码   
        if m:
            page = str(m.group(1))
            pages.append(page)

            title = line[:len(line)-len(page)] # 去掉页码
            titles.append(title)
        else:
            pages.append(1)
            titles.append(line)

    # print(titles)
    # print(levels)
    # print(pages)
    return titles, levels, pages

def _get_parent_bookmark(current_indent, history_indent, bookmarks):
    '''The parent of A is the nearest bookmark whose level is smaller than A's
    '''
    assert len(history_indent) == len(bookmarks)
    if current_indent == 0:
        return None
    for i in range(len(history_indent) - 1, -1, -1):
        # len(history_indent) - 1   ===>   0
        if history_indent[i] < current_indent:
            return bookmarks[i]
    return None

def addBookmark(pdf_path, bookmark_txt_path, page_offset):
    if not os.path.exists(pdf_path):
        print("Error: No such file: {}".format(pdf_path))
        return
    if not os.path.exists(bookmark_txt_path):
        print("Error: No such file: {}".format(bookmark_txt_path))
        return

    try:
        with open(bookmark_txt_path, 'r', encoding='utf-8') as f:
            bookmark_lines = f.readlines()
    except UnicodeDecodeError:
        with open(bookmark_txt_path, 'r') as f:
            bookmark_lines = f.readlines()
    titles, levels, pages = _parse_bookmark(bookmark_lines)

    reader = PdfFileReader(pdf_path, strict=False)#  strict=False忽略一些错误
    writer = PdfFileWriter()
    writer.cloneDocumentFromReader(reader)

    maxPages = reader.getNumPages()
    bookmarks, history_level = [], []
    
    for i in range(0, len(titles)):
        title = titles[i]
        page = int(pages[i])
        level = levels[i]

        parent = _get_parent_bookmark(level, history_level, bookmarks)
        history_level.append(level)

        if page + page_offset >= maxPages:
            print("Error: page index out of range: %d >= %d" % (page + page_offset, maxPages))
            page = 0
        else:
            page += page_offset

        print('add title:' + title + ',page:' + str(page))

        new_bookmark = writer.addBookmark(title, page, parent)
        bookmarks.append(new_bookmark)

    out_path = os.path.splitext(pdf_path)[0] + '-new.pdf'
    with open(out_path,'wb') as f:
        writer.write(f)

    print("The bookmarks have been added to %s" % out_path)

def getCurrentPath():
    current_path = os.path.dirname(__file__)
    return current_path

if __name__ == "__main__":
    bookmark_file = getCurrentPath() + os.path.sep +  r'book.txt'
    pdf_file = getCurrentPath() + os.path.sep +  r'Delphi7 程序设计与开发技术大全.pdf'

    addBookmark(pdf_file, bookmark_file, 20)


