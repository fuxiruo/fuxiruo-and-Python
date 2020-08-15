#!/usr/bin/python3 
#coding=utf-8
from urllib.parse import urljoin

from lxml import etree
class HtmlParserByXpath(object):
    def parse(self, page_url, html_cont):
        if page_url is None or html_cont is None:
            return

        xpatch_data = etree.HTML(html_cont)

        new_urls = self._get_new_urls("https://baike.baidu.com", xpatch_data)
        new_data = self._get_new_data(page_url, xpatch_data)
        return new_urls, new_data

    def _get_new_urls(self, head_url, xpatch_data_in):
        new_urls = set()
        # 注意要在//a[starts-with(@href,"/item")]加上/@href，否者取不到东西
        links_url = xpatch_data_in.xpath('//html/body/div[3]/div[2]/div//a[starts-with(@href,"/item")]/@href')
        for href in links_url:
            new_url = href.strip()
            new_full_url = urljoin(head_url, new_url)
            new_urls.add(new_full_url)
        return new_urls

    def _get_new_data(self, page_url, xpatch_data_in):
        datas = {}

        datas['url'] = page_url

        title_node = xpatch_data_in.xpath('//html/body/div[3]/div[2]/div/div[2]/dl[1]/dd/h1/text()')
        if title_node is not None:
            datas['title'] = title_node[0]  # 返回的是只有一个元素的列表
        else:
            datas['title'] = ""

        summary = xpatch_data_in.xpath('//div[@class="lemma-summary"]')
        summary_texts = summary[0].xpath('string(.)')  # xpath取出指定多标签内所有文字text
        if summary_texts is not None:
            datas['summary'] = summary_texts
        else:
            datas['summary'] = ""

        return datas
