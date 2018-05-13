import socket
import threading
import time
import re
import requests

PORT = 1080

NUM = 0


def scanner(ip_list):
    """
    IP扫描函数
    :param ip_list:  IP列表
    """
    for ip in ip_list:
        # 创建socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        target_host = socket.gethostbyname(ip)  # get host
        # 建立TCP连接
        result = s.connect_ex((target_host, PORT))
        # 如果返回0表示连接成功
        if result == 0:

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
                    with open('./result.txt', 'a') as f:
                        f.write('%d\t%s\t%s\n' % (NUM, ip, location.group(1)))
                    lock.release()
            except:
                print(ip, '1080端口已打开，但需要账号密码授权！')
                continue

        s.close()


def ip_to_num(ip):
    ip = [int(x) for x in ip.split('.')]
    return ip[0] << 24 | ip[1] << 16 | ip[2] << 8 | ip[3]


def num_to_ip(num):
    return '%s.%s.%s.%s' % ((num & 0xff000000) >> 24,
                            (num & 0x00ff0000) >> 16,
                            (num & 0x0000ff00) >> 8,
                            num & 0x000000ff)


# ip1 起始地址 , ip2 结束地址
def get_ip(ip1, ip2):  # 返回IP字符串组列表
    return [num_to_ip(num) for num in range(ip_to_num(ip1), ip_to_num(ip2) + 1) if num & 0xff]


if __name__ == '__main__':

    ip_start = '172.29.0.0'

    ip_end = '172.29.241.255'

    thread_num = 1000  # 线程数量

    # 根据指定IP网段生成所有IP
    ip_all_list = get_ip(ip_start, ip_end)

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



