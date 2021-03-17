import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import EurobankgrItem
from itemloaders.processors import TakeFirst


base = 'https://www.eurobank.gr/el/api/newsjson/gethtml?contextId={951D221A-9DEC-477E-A114-C3F72BFAFF7D}&pg=%s'

class EurobankgrSpider(scrapy.Spider):
	name = 'eurobankgr'
	page = 1
	start_urls = [base % page]

	def parse(self, response):
		data = json.loads(response.text)
		html = scrapy.Selector(text=data['listItemsHtml'])
		post_pages = html.xpath('//a[@target="_self"]/@href').getall()
		print(post_pages)
		yield from response.follow_all(post_pages, self.parse_post)

		total_pages = data['totalCount']
		if self.page <= total_pages/9:
			self.page += 1
			yield response.follow(base % self.page, self.parse)


	def parse_post(self, response):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//article//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//div[@class="b-article__date"]/text()').get()

		item = ItemLoader(item=EurobankgrItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
