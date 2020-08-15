#!/usr/bin/python3 
#coding=utf-8
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup


class HtmlParser(object):
    def parse(self, page_url, html_cont):
        if page_url is None or html_cont is None:
            return

        soup = BeautifulSoup(html_cont, 'html.parser')
        new_urls = self._get_new_urls("https://baike.baidu.com", soup)
        new_data = self._get_new_data(page_url, soup)
        return new_urls, new_data

    def _get_new_urls(self, head_url, soup):
        new_urls = set()
        links = soup.find_all('a', href=re.compile(r"/item/"))
        for link in links:
            new_url = link['href']
            new_full_url = urljoin(head_url, new_url)
            new_urls.add(new_full_url)
        return new_urls

    def _get_new_data(self, page_url, soup):
        datas = {}
        datas['url'] = page_url
# <dd class="lemmaWgt-lemmaTitle-title" style="font-size: 13.8px ! important; line-height: 20.7px ! important;">
# <h1 style="font-size: 39.1px ! important; line-height: 44.965px ! important;">Python</h1>

        title_node = soup.find('dd', class_="lemmaWgt-lemmaTitle-title").find('h1')
        datas['title'] = title_node.get_text()

        summary_node = soup.find('div', class_="lemma-summary")
        datas['summary'] = summary_node

        return datas


