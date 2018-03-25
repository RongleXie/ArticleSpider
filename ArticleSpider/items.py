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
        value = datetime.datetime.strptime(value, "%Y/%m/%d").date()
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
