# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import JobboleArticleItem, ArticlespiderItemLoader
from ArticleSpider.utils import common
import datetime
from scrapy.loader import ItemLoader

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1、获取列表中的文章url交给scrapy下载并进行解析
        2、获取下一面的url并交给scrapy下载，然后交给parse进行解析
        :param response:
        :return:
        """
        # 获取列表中的文章url交给scrapy下载并进行解析
        post_nodes = response.css('#archive .floated-thumb .post-thumb a')
        for post_node in post_nodes:
            post_url = post_node.css('::attr(href)').extract_first("")
            img_url = post_node.css('img::attr(src)').extract_first("")
            yield Request(url=parse.urljoin(response.url,post_url), meta={"front_image_url":img_url}, callback=self.parse_detail)

        # 获取下一面的url并交给scrapy下载，然后交给parse进行解析
        next_url = response.css('.next.page-numbers ::attr(href)').extract_first()
        if(next_url):
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        # 通过xpath选择器提取字段
        # title = response.xpath('//*[@class="entry-header"]/h1/text()').extract()[0].strip().replace('·','').strip()
        # create_date = response.xpath('//*[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace('·','').strip()
        # praise_num = int(response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract()[0])
        # fav_nums = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract()[0]
        # fav_nums_match = re.match('.*(\d)+.*',fav_nums)
        # if(fav_nums_match):
        #     fav_nums = int(fav_nums_match.group(1))
        # else:
        #     fav_nums = int(0)
        # comment_nums = response.xpath('//a[@href="#article-comment"]/span/text()').extract()[0]
        # comment_nums_match = re.match('.*(\d)+.*',comment_nums)
        # if(comment_nums_match):
        #     comment_nums = int(comment_nums_match.group(1))
        # else:
        #     comment_nums = int(0)
        # content = response.xpath('//div[@class="entry"]').extract()[0]
        # tags_list = response.xpath('//*[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        # tags_list = [element for element in tags_list if not element.strip().endswith("评论")]
        # tags = ','.join(tags_list)

        # article_item = JobboleArticleItem()
        #
        # #通过css选择器提取字段
        # front_image_url = response.meta.get("front_image_url", "") #文章封面图
        #
        # title = response.css('.entry-header h1::text').extract()[0].strip().replace('·','').strip()
        #
        # create_date = response.css('p.entry-meta-hide-on-mobile::text').extract()[0].strip().replace('·','').strip()
        #
        # praise_nums = int(response.css('span.vote-post-up h10::text').extract()[0])
        #
        # fav_nums = response.css('span.bookmark-btn::text').extract()[0]
        # fav_nums_match = re.match('.*(\d)+.*', fav_nums)
        # if (fav_nums_match):
        #     fav_nums = int(fav_nums_match.group(1))
        # else:
        #     fav_nums = int(0)
        #
        # comment_nums = response.css('a[href="#article-comment"] span::text').extract()[0]
        # comment_nums_match = re.match('.*(\d)+.*', comment_nums)
        # if (comment_nums_match):
        #     comment_nums = int(comment_nums_match.group(1))
        # else:
        #     comment_nums = int(0)
        #
        # content = response.css('div.entry').extract()[0]
        #
        # tags_list = response.css('p.entry-meta-hide-on-mobile a::text').extract()
        # tags_list = [element for element in tags_list if not element.strip().endswith("评论")]
        # tags = ','.join(tags_list)
        #
        # article_item["title"] = title
        # article_item["url"] = response.url
        # article_item["url_object_id"] = common.md5(response.url)
        # try:
        #     create_date = datetime.datetime.strptime(create_date, "%Y/%m/%d").date()
        # except Exception as e:
        #     create_date = datetime.datetime.now()
        # article_item["create_date"] = create_date
        # article_item["front_image_url"] = [front_image_url]
        # article_item["praise_nums"] = praise_nums
        # article_item["comment_nums"] = comment_nums
        # article_item["fav_nums"] = fav_nums
        # article_item["tags"] = tags
        # article_item["content"] = content

        # 通过css选择器提取字段
        front_image_url = response.meta.get("front_image_url", "")  # 文章封面图

        # 通过ItemLoader加载Item
        iter_loader = ArticlespiderItemLoader(item=JobboleArticleItem(), response=response)
        iter_loader.add_css("title", ".entry-header h1::text")
        iter_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
        iter_loader.add_css("praise_nums", "span.vote-post-up h10::text")
        iter_loader.add_css("comment_nums", "a[href='#article-comment'] span::text")
        iter_loader.add_css("fav_nums", "span.bookmark-btn::text")
        iter_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
        iter_loader.add_css("content", "div.entry")
        iter_loader.add_value("url", response.url)
        iter_loader.add_value("url_object_id", common.md5(response.url))
        iter_loader.add_value("front_image_url", [front_image_url])

        article_item = iter_loader.load_item()
        yield article_item

