import os
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

start_urls = [c.strip() for c in open('input/input-urls.txt').readlines()]
if start_urls:
    if '/sales/search/' in start_urls[0]:
        spidername = "search_to_company_data"
    else:
        spidername = 'url_to_company_data'

process = CrawlerProcess(get_project_settings())
process.crawl(spidername, domain='linkedin.com')
process.start()