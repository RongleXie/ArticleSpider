# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import MySQLdb
import MySQLdb.cursors

from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open("article.json","w",encoding="utf-8")

    def process_item(self, item, spider):
        lines = json.dumps(dict(item),ensure_ascii=False)+ "\n"
        self.file.write(lines)
        return item

    def spider_closed(self,spider):
        self.file.close()


# 采用同步的方式存入Mysql数据库
class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect(host="127.0.0.1",user="root",password="950505",database="jobbole_article",charset="utf8",use_unicode = True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        sql = "insert into article(title,create_date,url,url_object_id,front_image_url,front_image_path,comment_nums,fav_nums,praise_nums,tags,content) " \
              "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        self.cursor.execute(sql,
                            (item["title"], item["create_date"], item["url"], item["url_object_id"],
                             item["front_image_url"], item["front_image_path"], item["comment_nums"],
                             item["fav_nums"], item["praise_nums"], item["tags"], item["content"]))
        self.conn.commit()
        return item


# 采用异步的方式存入Mysql数据库
class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(self,settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            password=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)
        return self(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变为异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        print(failure)

    def do_insert(self, cursor, item):
        sql = "insert into article(title,create_date,url,url_object_id,front_image_url,front_image_path,comment_nums,fav_nums,praise_nums,tags,content) " \
              "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql, (item.get("title",""),item.get("create_date",""), item.get("url",""),
                             item.get("url_object_id",""), item.get("front_image_url",""),
                             item.get("front_image_path",""), item.get("comment_nums",""),
                             item.get("fav_nums",""), item.get("praise_nums",""),
                             item.get("tags",""), item.get("content", "")))


class ArticlePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        # 判断有封面图片才做处理
        if "front_image_url" in item:
            for key,value in results:
                img_file_path = value['path']
                item["front_image_path"] = img_file_path
        return item
