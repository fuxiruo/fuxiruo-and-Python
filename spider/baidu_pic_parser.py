#!/usr/bin/python3 
# -*- coding: utf-8 -*-
import json
import urllib

from spider import html_downloader


class PicParserByXpatch(object):
    def get_pic_url_list(self, key_words, pages):
        url = "http://image.baidu.com/search/acjson"

        downloader = html_downloader.HtmlDownloader()
        urls_list = []
        key_word_list = []
        for key_word, page in zip(key_words, pages):
            params = []
            urls = []
            for i in range(30, 30*page+30, 30):
                params.append({
                    'tn': 'resultjson_com',
                    'ipn': 'rj',
                    'ct': 201326592,
                    'is': '',
                    'fp': 'result',
                    'queryWord': key_word,
                    'cl': 2,
                    'lm': -1,
                    'ie': 'utf-8',
                    'oe': 'utf-8',
                    'adpicid': '',
                    'st': -1,
                    'z': '',
                    'ic': 0,
                    'word': key_word,
                    's': '',
                    'se': '',
                    'tab': '',
                    'width': '',
                    'height': '',
                    'face': 0,
                    'istype': 2,
                    'qc': '',
                    'nc': 1,
                    'fr': '',
                    'pn': i,
                    'rn': 30,
                    'gsm': '1e',
                    '1488942260214': ''
                })

            for param in params:
                resp = downloader.get_with_params(url, param)
                json_data_list = json.loads(resp).get('data')
                for json_data in json_data_list:
                    if json_data.get('thumbURL') is not None:
                        urls.append(json_data.get('thumbURL'))

            urls_list.append(urls)
            key_word_list.append(key_word)

        return key_word_list, urls_list
