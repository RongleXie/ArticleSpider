# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import datetime
import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader
import re

from ArticleSpider.settings import SQL_DATETIME_FORMAT
from ArticleSpider.utils.common import extract_num


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ArticlespiderItemLoader(ItemLoader):
    # 自定义ItemLoader
    default_output_processor = TakeFirst()


# 转换日期
def convert_date(value):
    try:
        value = datetime.datetime.strptime(value.strip().replace('·','').strip(), "%Y/%m/%d").date()
    except Exception as e:
        value = datetime.datetime.now()
    return value


# 获取数字
def get_number(value):
    nums_match = re.match('.*(\d)+.*', value)
    if (nums_match):
        value = int(nums_match.group(1))
    else:
        value = 0
    return value


# 去年tags中提取的评论
def remove_commont_tags(value):
    if "评论" in value:
        return ""
    else:
        return value


# 直接返回值，不做其它处理
def return_value(value):
    return value

# 伯乐在线文章Item
class JobboleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(convert_date)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_number)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_number)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_number)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_commont_tags),
        output_processor=Join(",")
    )
    content = scrapy.Field()

    def make_data_clean(self):
        front_image_url = ""
        # content = remove_tags(self["content"])
        self["crawl_time"] = datetime.datetime.now(
        ).strftime(SQL_DATETIME_FORMAT)
        if self["front_image_url"]:
            self["front_image_url"] = self["front_image_url"][0]
        str = self["create_date"].strip().replace("·", "").strip()
        self["create_date"] = datetime.datetime.strptime(
            str, "%Y/%m/%d").date()
        nums = 0
        value = self["praise_nums"]
        match_re = re.match(".*?(\d+).*", value)
        if match_re:
            nums = int(match_re.group(1))
        else:
            nums = 0
        self["praise_nums"] = nums

    def get_insert_sql(self):
        insert_sql = """
            insert into jobbole_article(title, url, url_object_id,create_date, fav_nums, front_image_url, front_image_path,
            praise_nums, comment_nums, tags, content,crawl_time)
            VALUES (%s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s,%s) ON DUPLICATE KEY UPDATE fav_nums=VALUES(fav_nums),praise_nums=VALUES(praise_nums),comment_nums=VALUES(comment_nums),crawl_time=VALUES(crawl_time)
        """
        self.make_data_clean()
        params = (
            self["title"],
            self["url"],
            self["url_object_id"],
            self["create_date"],
            self["fav_nums"],
            self["front_image_url"],
            self["front_image_path"],
            self["praise_nums"],
            self["comment_nums"],
            self["tags"],
            self["content"],
            self["crawl_time"]
        )
        return insert_sql, params


# 知乎问题Item
class ZhihuQuestionItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into zhihu_question 
            (zhihu_id,topics,title,url,content,answer_num,comments_num,watch_user_num,click_num,crawl_time) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num), comments_num=VALUES(comments_num),
              watch_user_num=VALUES(watch_user_num), click_num=VALUES(click_num)
        """
        zhihu_id = self["zhihu_id"][0]
        topics = ",".join(self["topics"])
        url = self["url"][0]
        title = "".join(self["title"])
        try:
            content = "".join(self["content"])
        except BaseException:
            content = "无"
        try:
            answer_num = extract_num("".join(self["answer_num"]))
        except BaseException:
            answer_num = 0
        comments_num = extract_num("".join(self["comments_num"]))

        if len(self["watch_user_num"]) == 2:
            watch_user_num = extract_num(self["watch_user_num"][0])
            click_num = extract_num(self["watch_user_num"][1])
        else:
            watch_user_num = extract_num(self["watch_user_num"][0])
            click_num = 0

        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        params = (
            zhihu_id,
            topics,
            url,
            title,
            content,
            answer_num,
            comments_num,
            watch_user_num,
            click_num,
            crawl_time)

        return insert_sql, params

# 知乎问题回答Item
class ZhihuAnswerItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    author_name = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        # 插入知乎answer表的sql语句
        insert_sql = """
            insert into zhihu_answer(zhihu_id, url, question_id, author_id, content, praise_num, comments_num,
              create_time, update_time, crawl_time,author_name
              ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
              ON DUPLICATE KEY UPDATE content=VALUES(content), comments_num=VALUES(comments_num), praise_num=VALUES(praise_num),
              update_time=VALUES(update_time), author_name=VALUES(author_name)
        """

        create_time = datetime.datetime.fromtimestamp(
            self["create_time"]).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(
            self["update_time"]).strftime(SQL_DATETIME_FORMAT)
        params = (
            self["zhihu_id"], self["url"], self["question_id"],
            self["author_id"], self["content"], self["praise_num"],
            self["comments_num"], create_time, update_time,
            self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
            self["author_name"],
        )

        return insert_sql, params
