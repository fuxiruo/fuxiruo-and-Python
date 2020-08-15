#!/usr/bin/python3 
#coding=utf-8
import datetime
import time

import os

from spider import url_manager, html_downloader, html_parser, spider_outputer, html_parser_by_xpath, \
    movie_parser_by_xpath, movie_outputer, blog_sina_parser_by_xpath, baidu_aip_ocr, baidu_pic_parser


class SpiderMain(object):
    def __init__(self):
        self.urls = url_manager.UrlManager()
        self.downloader = html_downloader.HtmlDownloader()
        # self.parser = html_parser.HtmlParser()
        self.parser = html_parser_by_xpath.HtmlParserByXpath()
        self.outputer = spider_outputer.HtmlOutputer()

    def craw(self, url):
        count = 1
        self.urls.add_url(url)
        while self.urls.has_new_url():
            try:
                new_url = self.urls.pop_url()
                print("craw:", count, " url:", new_url)
                html_cont = self.downloader.downloader(new_url)
                new_urls, new_data = self.parser.parse(new_url, html_cont)
                self.urls.add_urls(new_urls)
                self.outputer.collect_data(new_data)
                count = count + 1

                if count == 100:
                    break
            except Exception as e:
                print("Exception:" + repr(e))
                print("craw fail:" + new_url)

        self.outputer.output_html()


class SpiderMovieDytt(object):
    def __init__(self):
        self.downloader = html_downloader.HtmlDownloader()
        self.parser = movie_parser_by_xpath.MovieParserByXpatch()
        self.outputer = movie_outputer.MovieOutputer()

    def craw(self, main_url):
        # 先把主页面的内容下载下来
        html_main = self.downloader.download_with_para('gbk', main_url)
        html_url_lists = self.parser.parser_html_url_list("https://www.dy2018.com", html_main)

        count = 0
        while len(html_url_lists):
            html_now_url = html_url_lists.pop(0)
            html_now = self.downloader.download_with_para('gbk', html_now_url)
            # 解析主页面电影标题的URLS
            movie_titles, movie_title_urls = self.parser.parse_movie_title_urls("https://www.dy2018.com", html_now)
            while len(movie_titles) and len(movie_title_urls):
                try:
                    movie_title_url = movie_title_urls.pop(0)
                    movie_title = movie_titles.pop(0)
                    # 下载电影标题点击进去后的页面
                    movie_html = self.downloader.download_with_para('gbk', movie_title_url)
                    movie_thunder_url = self.parser.parse_movie_thunder_url(main_url, movie_html)
                    self.outputer.collect_data(movie_title, movie_thunder_url)

                except Exception as e:
                    print("Exception:" + repr(e))
                    print("craw fail:" + movie_title + "" + movie_thunder_url)
            count = count + 1
            if count == 2:
                break
            time.sleep(0.01)

        self.outputer.output_movie()


class SpiderBlogSina(object):
    def __init__(self):
        self.downloader = html_downloader.HtmlDownloader()
        self.parser = blog_sina_parser_by_xpath.PicParserByXpatch()
        self.outputer = spider_outputer.PicOutputer()
        self.ocrer = baidu_aip_ocr.PicOcrer()

    def craw(self, start_urls):
        for url in start_urls:
            html_main = self.downloader.download_with_para('utf-8', url)
            pic_url_lists = self.parser.parser_pic_url_list(html_main)
            save_path = "R:/Pic/"

            if not os.path.exists(save_path):
                os.mkdir(save_path)
            for pic_url in pic_url_lists:
                print("pic url:{}".format(pic_url))
                pic_name = save_path + pic_url.split('/')[-1] + ".jpeg"
                # pic_data = self.downloader.download(pic_url)
                # self.outputer.output_pic(pic_name, pic_data)
                if self.downloader.download_pic(pic_url, pic_name):
                    start = datetime.datetime.now()
                    pic_chars = self.ocrer.basic_ocr(pic_name)
                    end = datetime.datetime.now()
                    print("ocr time:{}".format(end - start))
                    if pic_chars['words_result']:
                        name = pic_chars['words_result'][0]['words'].replace('/', ' ')
                        new_pic_name = save_path + pic_url.split('/')[-1] + name + ".jpeg"
                        if os.path.exists(new_pic_name):
                            print("file exist:%s" % new_pic_name)
                            break
                        os.rename(pic_name, new_pic_name)


class SpiderBaiduPic(object):
    def __init__(self):
        self.downloader = html_downloader.HtmlDownloader()
        self.parser = baidu_pic_parser.PicParserByXpatch()
        self.outputer = spider_outputer.PicOutputer()

    def craw(self, key_words, pages, save_path):
        key_word_list, pic_url_list = self.parser.get_pic_url_list(key_words, pages)
        count = 0
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        for key_word, pic_urls in zip(key_word_list, pic_url_list):
            for pic_url in pic_urls:
                print("pic url:{}".format(pic_url))
                pic_name = save_path + key_word + str(count) + ".jpeg"
                pic_data = self.downloader.download(pic_url)
                if pic_data is not None:
                    self.outputer.output_pic(pic_name, pic_data)
                    count = count + 1


if __name__ == '__main__':
    root_url = "https://www.dy2018.com/html/gndy/dyzz/index.html"
    # obj_spider = SpiderMain()
    start_urls = ["http://blog.sina.com.cn/s/blog_68c08bcf0102dz7h.html",
                  "http://blog.sina.com.cn/s/blog_68c08bcf0102e3ud.html"]
    # obj_spider = SpiderMovieDytt()
    # obj_spider = SpiderBlogSina()
    # obj_spider.craw(start_urls)
    obj_spider = SpiderBaiduPic()
    key_words = {"多肉", "福"}
    pages = {2, 1}
    obj_spider.craw(key_words, pages, "R:/Pic/")

