import socket
import threading
import time
import re
import requests


PORT = 1080
NUM = 0


def scanner(ip_list):
    for ip in ip_list:
        try:
            my_proxies = {"http": 'http://' + ip + ':1080', "https": 'https://' + ip + ':1080'}
            url = "https://ip.cn/"
            resp = requests.get(url, proxies=my_proxies, timeout=6)
            resp.encoding = 'utf-8'
            result = resp.text
            location = re.search(r'<p>所在地理位置：<code>(.*?)</code>', result, re.M | re.I)
            if location:
                lock.acquire()
                global NUM
                NUM = NUM + 1
                print('ip:%s  location:%s' % (ip, location.group(1)))
                with open('./result2.txt', 'a') as f:
                    f.write('%d\t%s\t%s\n' % (NUM, ip, location.group(1)))
                lock.release()
        except Exception:
            print(ip, '1080端口已打开，但需要账号密码授权！')
            continue


if __name__ == '__main__':

    thread_num = 30  # 线程数量
    ip_all_list = []
    with open('./172.29网段.txt', 'r') as f:
        for line in f.readlines():
            ip_all_list.append(line.split(':')[0])

    list_len = len(ip_all_list)

    print('待扫描的IP数量：', list_len)
    print('开启的线程数量：', thread_num)
    n = list_len + (thread_num - 1) // thread_num  # 每个线程跑的IP数量

    print('----------------- 扫描开始 -----------------')

    lock = threading.Lock()  # 获取线程锁

    thread_pool = []  # 线程池[线程集合]
    # 给每个线程分配任务
    time_start = time.clock()
    start = 0
    while True:
        temp = ip_all_list[start:start + n]
        if len(temp) > 0:
            t = threading.Thread(target=scanner, args=(temp,))
            t.start()
            thread_pool.append(t)  # 加入线程池
            start = start + n
        else:
            break
    # 主线程等待所有的子线程执行完毕
    for th in thread_pool:
        th.join()

    time_end = time.clock()
    print('----------------- 扫描完成 -----------------')
    print('扫描耗时: %f s' % (time_end - time_start))
