# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
import codecs
import json
from  scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors
from ArticleSpider.items import JobBoleArticle,ZhihuQuestion,ZhihuAnswer

class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item

class JsonWithEncodingPipeline(object):
    #自定义json文件的导出
    def __init__(self):
        self.file =codecs.open('article.json','w',encoding='utf-8')
    def process_item(self, item, spider):
        lines = json.dumps(dict(item),ensure_ascii=False)+'\n'
        self.file.write(lines)
        return item
    def spider_close(self,spider):
        self.file.close()
#同步存储
# class MysqlPipeline(object):
#     def __init__(self):
#         self.conn = MySQLdb.connect('127.0.0.1',"root","0319",'article_spider',charset= "utf8",use_unicode=True)
#         self.cursor = self.conn.cursor()
#     def process_item(self, item, spider):
#         insert_sql, params = item.items_do_insert()
#         self.cursor.execute(insert_sql,params)
#         self.conn.commit()
#         return item
#异步存储
class MysqlTwistedPipeline():
    def __init__(self,dbpool):
        self.dbpool = dbpool
    @classmethod
    def from_settings(cls,settings):
        dbparams = dict(
            host = settings['MYSQL_HOST'],
            user = settings['MYSQL_USER'],
            passwd = settings['MYSQL_PASSWORD'],
            db = settings['MYSQL_DBNAME'],
            charset = "utf8",
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode = True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb",**dbparams,)
        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert,item)
        query.addErrback(self.hand_error,item,spider)
        return item
    def hand_error(self,failure,item,spider):
        print(failure)
        pass
    def do_insert(self,cursor,item):
        insert_sql,params = item.items_do_insert()
        cursor.execute(insert_sql, params)

class JsonExporterPipeline(object):
    def __init__(self):
        #调用scrapy提供的jsonexprot导出json文件
        self.file = open("articleexporter.json","wb")
        self.exporter = JsonItemExporter(self.file,encoding = 'utf-8',ensure_ascii=False)
        self.exporter.start_exporting()
    def close_spider(self):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
            for ok ,value in results:
                imagepath = value['path']
            item['image_path'] = imagepath
            return item

