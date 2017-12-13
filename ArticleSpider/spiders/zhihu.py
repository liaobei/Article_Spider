# -*- coding: utf-8 -*-
import scrapy
import requests
import http.cookiejar as cookielib
from scrapy.loader import ItemLoader
import re
import json
import time
import os
import datetime
from urllib import parse
from PIL import Image
from ArticleSpider.items import ZhihuQuestion,ZhihuAnswer
session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename = "cookies.txt")
class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3236.0 Safari/537.36"
    answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"
    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhihu.com/",
        "User-Agent": agent
    }

    headers["X-Requested-With"] = "XMLHttpRequest"
    def parse(self, response):
        #提取htmlurl中所有url
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url,url) for url in all_urls]
        all_urls= filter(lambda x:True if x.startswith("https") and "question" in x and "invited" not in x else False,all_urls)
        all_urls = [x for x in all_urls]
        for url in all_urls:
            match_obj  = re.match('(.*zhihu.com/question/(\d+))(/answer/(\d+)|$)',url)
            if match_obj:
                url = match_obj.group(1)
                question_id = match_obj.group(2)
                if match_obj.group(4):
                    answer_id = match_obj.group(4)
                yield scrapy.Request(url=url,dont_filter=True,headers=self.headers,meta={"question_id":question_id},callback=self.parse_question)
                # break

    def parse_question(self,response):
        QuestionItem = ItemLoader(item=ZhihuQuestion(),response= response)
        if "QuestionHeader-title" in response.text:
            watch_user_num=response.xpath('//div[2][contains(@class,"NumberBoard")]/text()').extract()[0]
            click_num = response.xpath('//div[2][contains(@class,"NumberBoard")]/text()').extract()[1]
            QuestionItem.add_xpath("topics",'//div[@class="Popover"]/div/text()')
            QuestionItem.add_xpath("title", '//h1[@class="QuestionHeader-title"]/text()')
            QuestionItem.add_value("url", response.url)
            QuestionItem.add_value("zhihu_id",response.meta.get("question_id"))
            QuestionItem.add_xpath("content",'//span[@class="RichText"]/text()')
            QuestionItem.add_xpath("comments_num",'//div[@class="QuestionHeader-Comment"]/button/text()')
            QuestionItem.add_value("watch_user_num",watch_user_num)
            QuestionItem.add_value("click_num",click_num)
            QuestionItem.add_xpath("answer_num", '//h4[@class="List-headerText"]/span/text()')

        answer_url = self.answer_url.format(response.meta.get("question_id"),20,0)
        self.headers["authorization"] = "Bearer 2|1:0|10:1512721118|4:z_c0|92:Mi4xWW5aWEFnQUFBQUFBTUlJeEt3eWZEQ1lBQUFCZ0FsVk4zcGdYV3dDaUhseVhDRk54WmJUc0VaZWdCdFJkY2tSWHlB|994b330c4a85af5bc419a6c8bfdf349cc6a8f4373df25ec336618f216f354162"
        yield scrapy.Request(url=answer_url,dont_filter=True,headers=self.headers,callback=self.parse_answer)
        yield QuestionItem.load_item()

    def parse_answer(self,response):
        answer_data = json.loads(response.text)
        is_end = answer_data['paging']['is_end']
        totals = answer_data['paging']['totals']
        next_url = answer_data['paging']['next']
        for data in answer_data["data"]:
            AnswerItem = ItemLoader(item=ZhihuAnswer(),response=response)
            AnswerItem.add_value("zhihu_id",data["id"])
            AnswerItem.add_value("url", data["url"])
            AnswerItem.add_value("question_id", data["question"]["id"])
            AnswerItem.add_value("author_id", data["author"]["id"] if "author" in data else None)
            AnswerItem.add_value("content", data["content"])
            AnswerItem.add_value("praise_num", data["voteup_count"])
            AnswerItem.add_value("comments_num", data["comment_count"])
            AnswerItem.add_value("create_time",data["created_time"])
            AnswerItem.add_value("update_time", data["updated_time"])
            AnswerItem.add_value("crawl_time", datetime.datetime.now())

        if not is_end:
            yield scrapy.Request(url=next_url,dont_filter=True,headers=self.headers,callback=self.parse_answer)
        yield AnswerItem.load_item()

    def start_requests(self):
        t = str(int(time.time() * 1000))
        captcha_url = 'http://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
        yield scrapy.Request(url = captcha_url,dont_filter=True,headers=self.headers,meta={"cookiejar":1},callback=self.request_captcha)


    def request_captcha(self,response):
        with open('captcha.jpg', 'wb') as f:
            f.write(response.body)
            f.close()
            # 用pillow 的 Image 显示验证码
            # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入
        try:
            im = Image.open('captcha.jpg')
            im.show()
            im.close()
        except:
            print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))

        captcha = input("please input the captcha\n>")

        yield scrapy.Request(url = "https://www.zhihu.com/",dont_filter=True,headers=self.headers,meta={'captcha':captcha,"cookiejar":response.meta['cookiejar']},callback=self.login )

    def login(self,response):
        response_text = response.text
        match_obj = re.match('.*name="_xsrf" value="(.*?)"', response_text, re.DOTALL)
        if match_obj:
            xsrf = (match_obj.group(1))
        captcha= response.meta.get("captcha","")

        if xsrf:
            post_url = "https://www.zhihu.com/login/phone_num"
            post_data = {
                "_xsrf": xsrf,
                "phone_num": "17770030411",
                "password": "19950319",
                "captcha" : captcha
            }

            yield scrapy.FormRequest(
                url=post_url,
                meta={"cookiejar":response.meta['cookiejar']},
                headers=self.headers,
                formdata=post_data,
                callback=self.check_login
            )

    # def login_after_captcha(self,response):
    #     post_data = response.meta.get("post_data", {})
    #     # captcha =
    #     # post_data["captcha"] = self.get_captcha()
    #     post_url = 'https://www.zhihu.com/login/phone_num'
    #     print(post_data)
    #
    #     return [scrapy.FormRequest(
    #         post_url,
    #         headers=self.headers,
    #         formdata=post_data,
    #         callback=self.check_login
    #     )]

    def check_login(self,response):
        text_json = json.loads(response.text)
        if "msg" in text_json and text_json["msg"] == "登录成功":
            for url in self.start_urls:
                yield scrapy.Request(url=url,dont_filter=True,meta={"cookiejar":response.meta['cookiejar']},headers=self.headers,callback=self.parse)
        else:
            pass




    # def get_captcha(self):
    #     t = str(int(time.time() * 1000))
    #     captcha_url = 'http://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
    #     r = session.get(captcha_url, headers=self.headers)
    #     with open('captcha.jpg', 'wb') as f:
    #         f.write(r.content)
    #         f.close()
    #     # 用pillow 的 Image 显示验证码
    #     # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入
    #     try:
    #         im = Image.open('captcha.jpg')
    #         im.show()
    #         im.close()
    #     except:
    #         print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
    #     captcha = input("please input the captcha\n>")
    #     return captcha
