import requests
from scrapy.selector import Selector
import MySQLdb
conn = MySQLdb.connect(host="127.0.0.1",user="root",passwd ="0319",db="article_spider",charset="utf8")
cursor = conn.cursor()
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0"}
def crawl_ips():

    re = requests.get(url="http://www.xicidaili.com/nn",headers=headers)
    select = Selector(text = re.text)
    all_trs = select.xpath('//table[@id="ip_list"]//tr')
    ip_list = []
    for tr in all_trs[1:]:
        ip = tr.xpath('td[2]/text()').extract_first()
        port = tr.xpath('td[3]/text()').extract_first()
        speed = float(tr.xpath('td[7]/div/@title').extract_first().split("秒")[0])
        ip_type = tr.xpath('td[6]/text()').extract_first()
        ip_list.append((ip,port,speed,ip_type))

    for ip_info in ip_list:
        cursor.execute("insert into proxy_ip(ip,port,speed,ip_type) values('{0}','{1}','{2}','{3}')".format(ip_info[0],ip_info[1],ip_info[2],ip_info[3]))
    conn.commit()

class GetIP(object):
    def delete_ip(self,ip,port):
        delete_sql = """delete from proxy_ip WHERE ip = {0} and port = {1}""".format(ip,port)
        cursor.execute(delete_sql)
    def judge_ip(self,ip ,port):
        req_url = "https://www.baidu.com"
        response = requests.get(url=req_url,proxies={"http":"http://{0}:{1}".format(ip,port)})
        code = response.status_code
        if code>=200 and code<300:
            print("right ip")
            return True
        else:
            self.delete_ip(ip,port)


    def get_random_ip(self):
        get_sql = """select ip,port from proxy_ip ORDER BY RAND() limit 1"""
        result = cursor.execute(get_sql)
        for info in cursor.fetchall():
            ip = info[0]
            port = info[1]
            result = self.judge_ip(ip,port)
            if result:
                return "http://{0}:{1}".format(ip,port)
            else:
                self.get_random_ip()


if __name__ == "__main__":
    print(GetIP().get_random_ip())