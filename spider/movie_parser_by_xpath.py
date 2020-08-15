#!/usr/bin/python3 
#coding=utf-8
from urllib.parse import urljoin

from lxml import etree


class MovieParserByXpatch(object):
    def parse_movie_title_urls(self, head_url, html_cont):
        xpath_data = etree.HTML(html_cont)

        movie_titles, movie_urls = self.get_movie_titles_and_urls(head_url, xpath_data)

        return movie_titles, movie_urls

    def get_movie_titles_and_urls(self, root_url, xpath_data):
        movie_titles = []
        movie_urls = []
        movie_title_nodes = xpath_data.xpath(".//*[@id='header']//table[*]//a[@title]")
        for movie_title_node in movie_title_nodes:
            new_url = movie_title_node.attrib.get("href").strip()
            new_full_url = urljoin(root_url, new_url)
            movie_title = movie_title_node.attrib.get("title").strip()
            # print(movie_title, new_full_url)
            movie_titles.append(movie_title)
            movie_urls.append(new_full_url)

        return movie_titles, movie_urls

    def parse_movie_thunder_url(self, main_url, movie_html):
        xpath_data = etree.HTML(movie_html)
        movie_title_nodes = xpath_data.xpath(".//table[*]/tbody//a/@href")
        if len(movie_title_nodes) == 0:
            return ""
        thunder_url = movie_title_nodes[0].strip()  # 可能有多个下载连接，只取其中一个
        return thunder_url

    def parser_html_url_list(self, root_url, html_main):
        xpath_data = etree.HTML(html_main)
        links = xpath_data.xpath(".//*[@id='header']//select//option/@value")
        html_list = []
        for link in links:
            new_full_url = urljoin(root_url, link)
            html_list.append(new_full_url)
        return html_list

