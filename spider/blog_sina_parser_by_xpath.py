#!/usr/bin/python3 
# -*- coding: utf-8 -*-

from lxml import etree


class PicParserByXpatch(object):
    def parser_pic_url_list(self, html_main):
        xpath_data = etree.HTML(html_main)
        links = xpath_data.xpath(".//*[@id='sina_keyword_ad_area2']//a[*]/img/@real_src")
        return links
