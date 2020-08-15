#!/usr/bin/python3 
#coding=utf-8


class HtmlOutputer(object):
    def __init__(self):
        self.datas = []

    def collect_data(self, data):
        if data is None:
            return
        self.datas.append(data)

    def output_html(self):
        fout = open('output.html', 'w', encoding='utf-8')
        fout.write("<html>")
        fout.write('<meta charset=\'utf-8\'>')
        fout.write("<body>")
        fout.write('<table border="1">')

        for data in self.datas:
            fout.write("<tr>")
            url = '<a  href="' + data['url'] + '"> ' + data['url'] + ' </a>'
            fout.write("<td>%s</td>" % url)
            fout.write("<td>%s</td>" % data['title'])
            fout.write("<td>%s</td>" % data['summary'])
            fout.write("</tr>")

        fout.write("</table>")
        fout.write("</body>")
        fout.write("</html>")
        fout.close()


class PicOutputer(object):
    def output_pic(self, file_name, pic_data):
        try:
            with open(file_name, 'wb') as f:
                f.write(pic_data)
                f.flush()
                print("Save OK:{}".format(file_name))
        except Exception as e:
            print("Exception:" + repr(e))
            print("Save Fail:{}".format(file_name))
