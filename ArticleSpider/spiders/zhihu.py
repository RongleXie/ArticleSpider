# -*- coding: utf-8 -*-
"""
@version: 3.6
@author: ronglexie
@license: Apache Licence
@contact: ronglexie@gmail.com
@site: http://www.ronglexie.top
@software: PyCharm
@file: zhihu.py
@time: 2018/3/28 21:27
"""
import json

import scrapy
import re
import execjs
import time
import json
from scrapy.loader import ItemLoader
from ArticleSpider.items import ZhihuQuestionItem
from ArticleSpider.items import ZhihuAnswerItem
import datetime
try:
    import urlparse as parse
except:
    from urllib import parse


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    # question的第一页answer的请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccollapsed_counts%2Creviewing_comments_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Crelationship.is_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.author.is_blocking%2Cis_blocked%2Cis_followed%2Cvoteup_count%2Cmessage_thread_token%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"

    phone = 'shouji'  # 手机号
    password = 'mima'  # 密码
    client_id = 'c3cef7c66a1843f8b3a9e6a1e3160e20'
    headers = {
        'authorization': 'oauth ' + client_id,
        'Host': 'www.zhihu.com',
        'Origin': 'https://www.zhihu.com',
        'Referer': 'https://www.zhihu.com/signup?next=%2F',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/63.0.3239.84 Safari/537.36'
    }
    # 自定义的知乎spider单独规则
    custom_settings = {
        "COOKIES_ENABLED": True,
        "DOWNLOAD_DELAY": 1.5,
    }

    def parse(self, response):
        # 提取所有页面的所有url，并跟踪这些url进行一步爬取
        # url格式为/question/xxx的地址就进行下载解析
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url,url) for url in all_urls]
        all_urls = filter(lambda x:True if x.startswith("https") else False, all_urls)
        for url in all_urls:
            match_object = re.match("(.*zhihu.com/question/(\d+)(/|$)).*", url)
            if(match_object):
                request_url = match_object.group(1)
                question_id = match_object.group(2)

                yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_question)
            # else:
                # yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    # 处理question页面，解析知乎问题Item
    def parse_question(self,response):
        if("QuestionHeader-title" in response.text):
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
            if match_obj:
                question_id = int(match_obj.group(2))
            # 处理新版本
            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            item_loader.add_css("title", "h1.QuestionHeader-title::text")
            item_loader.add_css("content", ".QuestionHeader-detail div div span::text")
            item_loader.add_value("url", response.url)
            item_loader.add_value("zhihu_id", question_id)
            item_loader.add_css("answer_num", ".List-headerText span::text")
            item_loader.add_css("comments_num", ".QuestionHeader-Comment button::text")
            # 这里一次把一列值提出来
            item_loader.add_css("watch_user_num", ".NumberBoard-itemValue::text")
            item_loader.add_css("topics", ".QuestionHeader-topics .Popover div::text")

            question_item = item_loader.load_item()
            pass
        else:
            # 处理老版本页面的item提取(好像已经没有老版页面了我这里放着保险一下)
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
            if match_obj:
                question_id = int(match_obj.group(2))

            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            # item_loader.add_css("title", ".zh-question-title h2 a::text")
            item_loader.add_xpath("title", "//*[@id='zh-question-title']/h2/a/text()|//*[@id='zh-question-title']/h2/span/text()")
            item_loader.add_css("content", "#zh-question-detail")
            item_loader.add_value("url", response.url)
            item_loader.add_value("zhihu_id", question_id)
            item_loader.add_css("answer_num", "#zh-question-answer-num::text")
            item_loader.add_css("comments_num", "#zh-question-meta-wrap a[name='addcomment']::text")
            # item_loader.add_css("watch_user_num", "#zh-question-side-header-wrap::text")
            item_loader.add_xpath("watch_user_num", "//*[@id='zh-question-side-header-wrap']/text()|//*[@class='zh-question-followers-sidebar']/div/a/strong/text()")
            item_loader.add_css("topics", ".zm-tag-editor-labels a::text")

            question_item = item_loader.load_item()
        # 发起向后台具体answer的接口请求
        yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0), headers=self.headers, callback=self.parse_answer)
        yield question_item

    # 处理answer页面，解析知乎问题回答Item
    def parse_answer(self, response):
        # 处理question的answer
        ans_json = json.loads(response.text)
        is_end = ans_json["paging"]["is_end"]
        next_url = ans_json["paging"]["next"]

        # 提取answer的具体字段
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["author_name"] = answer["author"]["name"] if "name" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["praise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()

            yield answer_item

        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)

    def start_requests(self):
        return [
            scrapy.Request(
                'https://www.zhihu.com/api/v3/oauth/captcha?lang=en',
                headers=self.headers,
                callback=self.login)]

    def login(self, response):
        captcha_info = json.loads(response.text)
        if captcha_info['show_captcha']:  # 出现验证码
            print('出现验证码')
        loginUrl = 'https://www.zhihu.com/api/v3/oauth/sign_in'
        timestamp = int(time.time() * 1000)
        fp = open('ArticleSpider/spiders/zhihu.js')
        js = fp.read()
        fp.close()
        ctx = execjs.compile(js)
        signature = ctx.call('getSignature', timestamp)
        params = {
            'client_id': self.client_id,
            'grant_type': 'password',
            'timestamp': str(timestamp),
            'source': 'com.zhihu.web',
            'signature': signature,
            'username': str(self.phone),
            'password': str(self.password),
            'captcha': '',
            'lang': 'cn',
            'ref_source': 'homepage',
            'utm_source': ''
        }

        yield scrapy.FormRequest(url=loginUrl, headers=self.headers, formdata=params, method='POST', callback=self.check_login)

    def check_login(self, response):
        # 验证服务器返回是否成功。
        HomeUrl = 'https://www.zhihu.com/'
        headers = {
            'Host': 'www.zhihu.com',
            'Referer': 'https://www.zhihu.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
        }
        print("登录成功")
        yield scrapy.Request(url=HomeUrl, headers=headers)