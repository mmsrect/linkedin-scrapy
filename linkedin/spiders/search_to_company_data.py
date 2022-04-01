import os
import re
import json
import math
import scrapy
import logging
import urllib.parse
from urllib.parse import urlparse
from urllib.parse import parse_qs
from urllib.parse import urlencode
from ..items import LinkedinItem

# convert search_url to api_url
def get_api_url(url, start=0, count=25):
    logging.info(f"Generating API url for: {url}")
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)['query'][0]

    try:
        sessionId = parse_qs(parsed_url.query)['sessionId'][0]
    except:
        trackingParam = parse_qs(parsed_url.query)['trackingParam'][0]
        sessionId = re.findall("\(sessionId:(.*?)\)",trackingParam)[0]

    # url in this function will either be the standard url, which wont have a "start param"
    # in which case start will be 0
    # or on second run onwards it will be response.url, which will have the start param
    # since the count is 100, we can move to next page by start+=100
    # also if start in url: it means it is an api url
    # here we dont need to parse reintegrate it. Doing that causes it to encode unneeded html entities
    # so simply replace start and return
    if 'start' in parse_qs(parsed_url.query):
        start = parse_qs(parsed_url.query)['start'][0]
        start = int(start)+count
        url = re.sub(r'start\=(\d+)',f'start={start}',url)
        return url

    params = {
        'q': 'searchQuery',
        'query': query,
        'start': start,
        'count': count,
        'trackingParam': f'(sessionId:{sessionId})',
        'decorationId': 'com.linkedin.sales.deco.desktop.searchv2.AccountSearchResult-1'
    }

    url = 'https://www.linkedin.com/sales-api/salesApiAccountSearch?'
    url = url + urlencode(params)
    url = urllib.parse.unquote(url)
    
    return url



class SearchToCompanyDataSpider(scrapy.Spider):
    name = 'search_to_company_data'
    allowed_domains = ['linkedin.com']
    start_urls = [c.strip() for c in open('input/input-urls.txt').readlines()]

    # get cookies from 1-input/cookies.txt
    try:
        rawcookies = open('input/cookies.txt').read().strip()
        if rawcookies == "enter_your_cookies_here":
            rawcookies = os.environ['cookies']
        cookies = json.loads(rawcookies)
        li_at = [c['value'] for c in cookies if c['name']=='li_at'][0]
        li_a = [c['value'] for c in cookies if c['name']=='li_a'][0]
        jsessionid = [[c['value'] for c in cookies if c['name']=='JSESSIONID'][0].replace('"','')]
        cookies = {'li_at':li_at, 'li_a':li_a, 'JSESSIONID':f'"{jsessionid[0]}"'}
        headers = {
            'Csrf-Token': jsessionid[0],
            'x-restli-protocol-version': '2.0.0',
            # 'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36'
            }
    except Exception as e:
        cookies = None
        logging.error("Error in loading cookies. Please copy cookies using the chrome extension")
        logging.error(e, exc_info=True)

    def start_requests(self):
        for url in self.start_urls:
            referer = url
            headers = self.headers
            headers['referer'] = referer
            url = get_api_url(url)
            logging.info(f"Visiting: {url}")
            request = scrapy.Request(
                url = url,
                headers=headers,
                cookies=self.cookies,
                callback=self.parse_api_url
            )
            yield request

    def parse_api_url(self,response):
        elements = response.json()['elements']
        paging = response.json()['paging']
        for element in elements:
            entityUrn = element.get('entityUrn')
            if entityUrn:
                old_linkedin_url = f"https://www.linkedin.com/company/{entityUrn.split(':')[-1]}/about/"
            else:
                old_linkedin_url = ''
            
            item = LinkedinItem()
            item['old_linkedin_url'] = old_linkedin_url
            logging.info(f"Storing: {item}")
            yield item
        
        # next page
        total_results = paging['total']
        max_start = math.ceil(total_results/25)*25
        max_start = min(max_start,1000)
        start = paging['start'] + 25
        if start < max_start:
            # the function below will always add 100 to start, if start!=0, hence call it only if start<max_start
            apiurl = get_api_url(response.url) # convert standard url to api url
            request = scrapy.Request(
                url = apiurl,
                cookies = self.cookies,
                headers = self.headers,
                callback = self.parse_api_url
            )
            yield request
