# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose,TakeFirst,Join
import  datetime
from scrapy.loader import ItemLoader
import re
from ArticleSpider.util.common import get_num
from ArticleSpider.settings import DATE_FORMATE,DATETIME_FORMATE
class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

def time_convert(value):
    try:
        create_time = datetime.datetime.strptime(value, '%Y/%m/%d').date()
    except Exception as e:
        create_time = datetime.datetime.now()
    return create_time
def get_nums(value):
    match_re = re.match(r'.*(\d+).*',value)
    if match_re:
        num = int(match_re.group(1))
    else:
        num = 0
    return num

def remove_comment_tags(value):
    if "评论" in value:
        return ""
    else :
        return value

def return_value(value):
    return value
class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

class JobBoleArticle(scrapy.Item):
    title = scrapy.Field(
        input_processor = MapCompose(lambda x:x+'.jobbole')
    )
    create_time = scrapy.Field(
        input_processor=MapCompose(time_convert),
    )
    url = scrapy.Field()
    author = scrapy.Field()
    url_object_id =scrapy.Field()
    image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor =Join(",")
    )
    content= scrapy.Field(
        output_processor=Join("\n")
    )

    def do_insert(self):
        insert_sql = """insert into jobbole_article(title,create_time,url,author,url_object_id,image_url, image_path,praise_nums, comment_nums,fav_nums,tags,content)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                       """
        params = (self['title'], self['create_time'], self['url'],self['author'], self['url_object_id'], self['image_url'], self['image_path'], self['praise_nums'], self['comment_nums'] , self['fav_nums'], self['tags'], self['content'])
        return insert_sql,params
class ZhihuAnswer(scrapy.Item):
    zhihu_id= scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()
    craw_update_time = scrapy.Field()

    def items_do_insert(self):
        insert_sql = """insert into zhihu_answer(zhihu_id,url,question_id,author_id,content,praise_num,comments_num,create_time,update_time,crawl_time)
                                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE content = VALUES(content),praise_num = VALUES(praise_num),
                                comments_num = VALUES(comments_num), update_time = VALUES(update_time)
                              """

        zhihu_id = self["zhihu_id"][0]
        url = self["url"][0]
        question_id = self["question_id"][0]
        author_id = self["author_id"][0]
        content = self["content"][0]
        praise_num = self["praise_num"][0]
        comments_num = self["comments_num"][0]
        create_time = datetime.date.fromtimestamp(self["create_time"][0]).strftime(DATE_FORMATE)
        updatetime = datetime.date.fromtimestamp(self["update_time"][0]).strftime(DATE_FORMATE)
        crawl_time= datetime.datetime.now().strftime(DATETIME_FORMATE)

        param = (zhihu_id, url, question_id, author_id, content, praise_num, comments_num, create_time, updatetime, crawl_time)
        return insert_sql, param


class ZhihuQuestion(scrapy.Item):
    zhihu_id =scrapy.Field()
    topics =scrapy.Field()
    url =scrapy.Field()
    title = scrapy.Field()
    content =scrapy.Field()
    create_time =scrapy.Field()
    update_time =scrapy.Field()
    answer_num =scrapy.Field()
    comments_num =scrapy.Field()
    watch_user_num =scrapy.Field()
    click_num =scrapy.Field()
    crawl_time =scrapy.Field()
    crawl_update_time = scrapy.Field()

    def items_do_insert(self):
        insert_sql = """insert into zhihu_question(zhihu_id,topics,url,title,content,answer_num,comments_num,watch_user_num,click_num,crawl_time)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE content = VALUES(content),answer_num = VALUES(answer_num),
                            comments_num = VALUES(comments_num),watch_user_num = VALUES(watch_user_num),click_num = VALUES(click_num)
                          """
        zhihu_id = int(self["zhihu_id"][0])
        title = self["title"][0]
        topics = "".join(self["topics"][0])
        url = "".join(self["url"][0])
        content = "".join(self["content"][0])
        answer_num = get_num(self["answer_num"][0])
        comments_num = get_num(self["comments_num"][0])
        watch_user_num = get_num(self["watch_user_num"][0])
        click_num = int(self["click_num"][0])
        crawl_time = datetime.datetime.now().strftime(DATETIME_FORMATE)
        param = (zhihu_id,topics,url,title,content,answer_num,comments_num,watch_user_num,click_num,crawl_time)

        return insert_sql,param