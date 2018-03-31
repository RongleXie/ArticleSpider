#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@version: 3.6
@author: ronglexie
@license: Apache Licence 
@contact: ronglexie@gmail.com
@site: http://www.ronglexie.top
@software: PyCharm
@file: crawl_xici_ip.py
@time: 2018/3/31 14:57
"""
import requests
from scrapy.selector import Selector
import MySQLdb

conn = MySQLdb.connect(host="127.0.0.1",
                       user="root",
                       password="950505",
                       database="scrapy_spider",
                       charset="utf8",
                       use_unicode=True)
cursor = conn.cursor()


def crawl_ips():
    url = "http://www.xicidaili.com/nn"
    headers = {
        'Host': 'www.xicidaili.com',
        'Origin': 'http://www.xicidaili.com/',
        'Referer': 'http://www.xicidaili.com/nn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/63.0.3239.84 Safari/537.36'
    }
    for i in range(1, 2000):
        response = requests.get('http://www.xicidaili.com/nn/{0}'.format(i), headers=headers)

        selector = Selector(text=response.text)
        trs = selector.css("#ip_list tr")
        ip_list = []

        for tr in trs[1:]:
            speed_str = tr .css(".bar::attr(title)").extract_first()
            if(speed_str):
                speed = float(speed_str.replace("秒", ""))
            all_text = tr.css("td::text").extract()
            ip = all_text[0]
            port = all_text[1]
            proxy_type = 'HTTP' #all_text[5]

            ip_list.append((ip, port, proxy_type, speed))

            for ip in ip_list:
                cursor.execute(
                    "insert into xici_proxy_ip (ip,port,speed,proxy_type) VALUES "
                    "('{0}','{1}','{2}','{3}') "
                    "ON DUPLICATE KEY UPDATE speed = VALUES(speed)".format(ip[0], ip[1], ip[3], ip[2])
                )
                conn.commit()


class GetIP(object):
    # 删除IP
    def delete_ip(ip, port):
        delete_sql = """
            delete from xici_proxy_ip where ip='{0}',port='{1}'
        """.format(ip, port)
        cursor.execute(delete_sql)
        conn.commit()
        return True


    # 检测IP是否可用
    def judge_ip(self, ip, port):
        http_url = "https://www.baidu.com"
        proxy_url = "http://{0}:{1}".format(ip, port)
        try:
            proxy_dict = {
                "http": proxy_url
            }
            response = requests.get(http_url, proxies=proxy_dict)
        except Exception as e:
            print("invalid ip and port")
            # self.delete_ip(ip, port)
            return False
        else:
            code = response.status_code
            if code >= 200 and code <= 300:
                print("effective ip")
                return True
            else:
                print("invalid ip and port")
                # self.delete_ip(ip, port)
                return False

    def get_random_ip(self):
        random_sql = """
            SELECT ip,port 
            FROM xici_proxy_ip 
            ORDER BY RAND() 
            LIMIT 1
        """

        result = cursor.execute(random_sql)
        if result:
            for ip_info in cursor.fetchall():
                ip = ip_info[0]
                port = ip_info[1]
                if(self.judge_ip(ip, port)):
                    return "http://{0}:{1}".format(ip, port)
                else:
                    return self.get_random_ip()


if __name__ == '__main__':
    # crawl_ips()
    # get_ip = GetIP()
    # get_ip.get_random_ip()
    pass
