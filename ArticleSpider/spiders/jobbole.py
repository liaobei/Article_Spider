# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import JobBoleArticle,ArticleItemLoader
from ArticleSpider.util.common import get_md5
class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        post_urls = response.xpath('//div[@id="archive"]/div/div/a')
        for post_url in post_urls:
            front_image_url = post_url.xpath('img/@src').extract_first("")
            target = post_url.xpath('@href').extract_first("")
            yield Request(url=parse.urljoin(response.url,target),meta={"front_image_url":front_image_url}, callback=self.parse_detail)
        nextpage = response.xpath('//div[contains(@class,"navigation")]/a[contains(@class,"next")]/@href').extract_first();
        if nextpage:
            yield Request(url=parse.urljoin(response.url,nextpage),callback=self.parse)


    def parse_detail(self, response):
        #xpath 提取方法，过于繁琐，建议使用ItemLoader
        # ArticleItem = JobBoleArticle()
        # title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first()
        # create_time = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract_first().strip().replace('·',' ').strip()
        # praise_nums = int(response.xpath('//div[@class="post-adds"]/span/h10/text()').extract()[0])
        #
        # fav_nums = re.match(r'.*(\d+).*',response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract()[0])
        # if fav_nums:
        #     fav_nums = int(fav_nums.group(1))
        # else:
        #     fav_nums = 0
        # comment_nums = re.match(r'.*(\d+).*', response.xpath('//a[contains(@href,"comment")]/span/text()').extract()[0])
        # if comment_nums:
        #     comment_nums = int(comment_nums.group(1))
        # else:
        #     comment_nums = 0
        # content =  response.xpath('//div[@class="entry"]/p/text()').extract();
        # tag_list =response.xpath('//p[contains(@class,"hide-on-mobile")]/a/text()').extract();
        # tag_list = [t for t in tag_list if not t.strip().endswith("评论")]
        # tags= ",".join(tag_list)
        # author = response.xpath('//div[@class="copyright-area"]/a/text()').extract_first()
        #
        # # ArticleItem["title"] = title
        # try:
        #     create_time = datetime.datetime.strptime(create_time,'%Y/%m/%d').date()
        # except Exception as e :
        #     create_time  = datetime.datetime.now()
        # ArticleItem["create_time"] = create_time
        # ArticleItem["praise_nums"] = praise_nums
        # ArticleItem["fav_nums"] = fav_nums
        # ArticleItem["comment_nums"] = comment_nums
        # ArticleItem["content"] = content
        # ArticleItem["tags"] = tags
        # ArticleItem["url_object_id"] = get_md5(response.url)
        # ArticleItem["image_url"] = [front_image_url]
        # ArticleItem["author"] = author
        # ArticleItem["url"] = response.url


        front_image_url = response.meta.get("front_image_url", "")
        item_loader = ArticleItemLoader(item=JobBoleArticle(),response=response)
        item_loader.add_xpath('title', '//div[@class="entry-header"]/h1/text()')
        item_loader.add_xpath('create_time','//p[@class="entry-meta-hide-on-mobile"]/text()')
        item_loader.add_xpath('praise_nums','//div[@class="post-adds"]/span/h10/text()')
        item_loader.add_xpath('fav_nums', '//span[contains(@class,"bookmark-btn")]/text()')
        item_loader.add_xpath('comment_nums','//a[contains(@href,"comment")]/span/text()')
        item_loader.add_xpath('content','//div[@class="entry"]//p/text()')
        item_loader.add_xpath('tags','//p[contains(@class,"hide-on-mobile")]/a/text()')
        item_loader.add_value('url_object_id',get_md5(response.url))
        item_loader.add_value('image_url',[front_image_url])
        item_loader.add_xpath('author','//div[@class="copyright-area"]/a/text()')
        item_loader.add_value('url',response.url)

        ArticleItem = item_loader.load_item()
        yield  ArticleItem

