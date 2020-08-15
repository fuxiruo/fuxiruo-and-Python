#!/usr/bin/python3 
#coding=utf-8

class MovieOutputer(object):
    def __init__(self):
        self.movie_datas = []

    def collect_data(self, movie_title, movie_thunder_url):
        movie_data = {}
        # print('{1}   {0}'.format(movie_thunder_url, movie_title))
        # print(movie_title + "   " + movie_thunder_url)
        print("%s   %s" % (movie_title, movie_thunder_url))
        movie_data['movie_title'] = movie_title
        movie_data['movie_thunder_url'] = movie_thunder_url
        self.movie_datas.append(movie_data)

    def output_movie(self):
        with open('output.html', 'w', encoding='utf-8') as fout:
            fout.write("<html>")
            fout.write('<meta charset=\'utf-8\'>')
            fout.write("<body>")
            fout.write('<table border="1">')

            for data in self.movie_datas:
                fout.write("<tr>")
                fout.write("<td>%s</td>" % data['movie_title'])
                # url = '<a  href="' + data['movie_thunder_url'] + '"> ' + data['movie_thunder_url'] + ' </a>'
                fout.write("<td>%s</td>" % data['movie_thunder_url'])
                fout.write("</tr>")

            fout.write("</table>")
            fout.write("</body>")
            fout.write("</html>")


