import logging
import time
import winsound
import uiautomator2 as u2
from collections import namedtuple

LOG_FORMAT = '[%(asctime)s][%(levelname)5s][%(module)s:%(funcName)s][%(threadName)10s:%(thread)5d]->%(message)s'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter(LOG_FORMAT)

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

Tofindobject = namedtuple('Tofindobject', ['type', 'value'])

def try_start_app(dev, app):
    '''尝试启动app'''
    try:
        app_list = dev.app_list_running()
        if app not in app_list:
            logger.debug('try start {}'.format(app))
            dev.app_start(app)
        pid = dev.app_wait(app) # 等待应用运行, return pid(int)
        if not pid:
            logger.debug("{} is not running".format(app))
            return False
        else:
            print("{} pid is {}".format(app, pid))
            return True
    except Exception as err:
        logger.error(str(err))
        return False

def try_in_target(dev, target_level):
    '''进入目标页面'''
    try_times = 0
    bfinal_level_found = False
    while try_times < 3 and not bfinal_level_found:
        try_times = try_times + 1
        logger.debug('try {} times'.format(try_times))
        for level, target in enumerate(target_level):
            if target.type == 'xpatch':
                btn = dev.xpath(target.value)
            else:
                btn = dev(textMatchs=target.value)
            if btn.click_exists(timeout=3):
                logger.debug("try in level {}".format(level))
                if not btn.wait_gone(timeout=3):
                    logger.debug("try in level {} fail".format(level))
                else:
                    logger.debug("in level {} succ".format(level))
                    if level==len(target_level)-1:
                        logger.debug("final level succ")
                        bfinal_level_found = True
                        break

        if not bfinal_level_found:
            logger.debug('back')
            dev.press("back")
            time.sleep(3)

def check_run_finish(dev, finish_marks, timeout=15):
    total_time = 0
    while total_time < timeout:
        start = time.time()
        for mark in finish_marks:
            if dev(textMatches='{}.*'.format(mark)).wait(timeout=0.5):
                logger.debug("完成")
                return True
            elif dev(descriptionContains=mark).wait(timeout=0.5):
                logger.debug("完成")
                return True
        end = time.time()
        total_time = end - start

    logger.debug("完成 超时")
    return False

def try_run(dev, actions, finish_marks):
    fail_times = 0
    while fail_times < 3:
        for action in actions:
            logger.debug("开始{}".format(action))
            go_browse = dev(textMatches='{}.*'.format(action))

            if go_browse.click_exists(timeout=0.5):
                print("{}".format(action))
                if not go_browse.wait_gone(timeout=3):
                    print("{}失败".format(action))
                    continue

                time.sleep(3)
                dev(scrollable=True).scroll(steps=5)
                time.sleep(3)
                dev(scrollable=True).scroll(steps=5)
                time.sleep(3)

                check_run_finish(dev, finish_marks)

                dev.press("back")
                time.sleep(3)
            else:
                fail_times = fail_times + 1

                btn_close = d(textMatches='开心收下.*')
                btn_close.click_exists(timeout=1)
                
                logger.debug("{}没找到".format(action))
                break

if __name__ == '__main__':
    try:
        u2.HTTP_TIMEOUT = 5
        d = u2.connect('192.168.1.103:5555')

        winsound.Beep(500,200)

        target_level = []
        target_level.append(Tofindobject('xpatch', '//*[@resource-id="com.taobao.taobao:id/rv_main_container"]/android.widget.FrameLayout[2]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[11]'))
        target_level.append(Tofindobject('xpatch', '赚糖领红包'))

        max_count = 3
        key_texts = ['去浏览']
        finish_marks = ['任务已完成', '喵糖已发放', '开心收下']
        while max_count > 0:
            max_count = max_count+1
            try_run(d, key_texts, finish_marks)
            try_in_target(d, target_level)

        winsound.Beep(500,1000)
    except Exception as err:
        print(err)
