#!/usr/bin/python3 
#coding=utf-8
import urllib.request
import gzip

class HtmlDownloader(object):
    def downloader(self, url):
        if url is None:
            return None

        resp = urllib.request.urlopen(url)
        if resp.getcode() != 200:
            return None

        return resp.read().decode('utf-8')

    def download(self, url):
        if url is None:
            return None

        req = urllib.request.Request(url)
        req.add_header('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0')
        try:
            resp = urllib.request.urlopen(req)
        except Exception as e:
            print("urlopen Exception:{}".format(e))
            return None
        if resp.getcode() != 200:
            print("download:" + url + "fail,code:" + resp.getcode())
            return None

        return resp.read()

    def download_with_para(self, decode_type, url, timeout):
        if url is None:
            return None

        req = urllib.request.Request(url)
        req.add_header('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0')
        req.add_header('Accept-Encoding', 'gzip, deflate')
        resp = urllib.request.urlopen(req, timeout=timeout)
        if resp.getcode() != 200:
            print("download:" + url + "fail,code:" + resp.getcode())
            return None

        if resp.getheader('Content-Encoding') == 'gzip':
            response = gzip.decompress(resp.read())
        else:
            response = resp.read()
        return response.decode(decode_type, errors='ignore')

    def urlretrieve_cbk(self, blocknum, bs, size):
        '''''回调函数
        @a:已经下载的数据块
        @b:数据块的大小
        @c:远程文件的大小
        '''
        per = 100.0 * blocknum * bs / size
        if per > 100:
            per = 100
        print('Downloading...:%.2f%%' % per)

    def download_pic(self, pic_url, pic_file):
        if urllib.request.urlretrieve(pic_url, pic_file, self.urlretrieve_cbk):
            print("Save OK:{}".format(pic_file))
            return True
        else:
            print("Save Fail:{}".format(pic_file))
            return False

    def get_with_params(self, url, params):
        url_params = urllib.parse.urlencode(params)
        req_url = url + "?" + url_params
        req = urllib.request.Request(req_url)
        req.add_header('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0')
        resp = urllib.request.urlopen(req)

        if resp.getcode() != 200:
            return None

        return resp.read().decode('utf-8')

