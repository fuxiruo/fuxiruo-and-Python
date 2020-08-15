#!/usr/bin/python3 
# -*- coding: utf-8 -*-
from aip import AipOcr


class PicOcrer(object):
    def __init__(self):
        self.APP_ID = '10824247'
        self.API_KEY = 'm3il8aWzYIaLfkzrTrBcnDCl'
        self.SECRET_KEY = 'BWTYLxXdYHapfNy7YfUpg2Vetqc6kHVV'
        self.client = AipOcr(self.APP_ID, self.API_KEY, self.SECRET_KEY)

    def get_file_content(self, file_path):
        try:
            with open(file_path, 'rb') as fp:
                return fp.read()
        except Exception as e:
            print("Exception:" + repr(e))
            print("get_file_content fail:" + file_path)

    def basic_ocr(self, file_path):
        img = self.get_file_content(file_path)
        return self.client.basicGeneral(img)
