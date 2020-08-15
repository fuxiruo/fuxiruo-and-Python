# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'

# %%
import os
os.sys.path.append('F:\KO\Python\Prj\Test\spider')


# %%
import html_downloader,html_parser,html_parser_by_xpath,movie_parser_by_xpath
from lxml import etree
import threading

# %%
downloader = html_downloader.HtmlDownloader()


# %%
all_movie_titles = []
lock_all_movie_titles = threading.Lock()
threads = []
threads_size = 10

def download_and_get_title(url):
    try:
        with lock_all_movie_titles:
            print("{} start".format(url))
        html_main = downloader.download_with_para('gbk', url, timeout=10)
        xpath_data = etree.HTML(html_main)
        titles = xpath_data.xpath('//*[@class="ulink" and @title]/@title')
        with lock_all_movie_titles:
            all_movie_titles.extend(titles)
            print("{} done".format(url))
    except Exception as err:
        print('{} {}'.format(url, err))

def download_and_get_title2(url):
    try:
        with lock_all_movie_titles:
            print("{} start".format(url))
        html_main = downloader.download_with_para('gbk', url, timeout=10)
        xpath_data = etree.HTML(html_main)
        titles = xpath_data.xpath('//*/table/tr[4]/td[1]/text()')
        with lock_all_movie_titles:
            all_movie_titles.extend(titles)
            print("{} done".format(url))
    except Exception as err:
        print('{} {}'.format(url, err))

def parse(urls, parse_func):
    for url in urls:
        url_wait_thread = True
        while url_wait_thread:
            if len(threads) < threads_size:
                new_thread = threading.Thread(target=parse_func, args=(url, ))
                threads.append(new_thread)
                new_thread.start()
                url_wait_thread = False

            for i in range(len(threads)-1, -1, -1):
                threads[i].join(timeout=0.1)
                if not threads[i].is_alive():
                    threads.pop(i)   
    
def filter_my_favorite_movie(title):
    tags = ['粤', '动画', '喜剧']
    for tag in tags:
        if not title.count(tag):
            return False
    return True

print('*'*50)
urls = ['https://www.dy2018.com/1/index.html']
urls.extend(['https://www.dy2018.com/1/index_{}.html'.format(x) for x in range(50) if x > 1])
parse(urls, download_and_get_title)

urls = ['https://www.dytt8.net/html/gndy/dyzz/list_23_{}.html'.format(x) for x in range(50) if x > 0]
# parse(urls, download_and_get_title2)

for i in range(len(threads)-1, -1, -1):
    threads[i].join()

my_favorite_movies = filter(filter_my_favorite_movie, all_movie_titles)
for movie in list(my_favorite_movies):
    print(' '*50)
    print(movie)


# %%


