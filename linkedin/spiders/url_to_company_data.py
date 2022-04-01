import os
import re
import json
import scrapy
import logging

# # find values for nested keys
# # print(list(find_values_for_nested_keys(d, 'id')))
# def find_values_for_nested_keys(node, kv):
#     if isinstance(node, list):
#         for i in node:
#             for x in find_values_for_nested_keys(i, kv):
#                yield x
#     elif isinstance(node, dict):
#         if kv in node:
#             yield node[kv]
#         for j in node.values():
#             for x in find_values_for_nested_keys(j, kv):
#                 yield x


class UrlToCompanyDataSpider(scrapy.Spider):
    name = 'url_to_company_data'
    allowed_domains = ['linkedin.com']
    start_urls = [c.strip() for c in open('input/input-urls.txt').readlines()] # get urls from input file

    # get cookies from 1-input/cookies.txt
    rawcookies = open('input/cookies.txt').read().strip()
    if rawcookies == "enter_your_cookies_here":
        rawcookies = os.environ['cookies']
    if not rawcookies.endswith(';'): rawcookies+=';'

    try:
        li_at = re.findall('(li\_at\=)(.+?)(\;\ )',rawcookies)[0][1]
        # li_a = re.findall('(li\_a\=)(.+?)(\;\ ?)',rawcookies)[0][1]
        jsessionid = re.findall('(JSESSIONID\=\")(ajax\:\d+)(\")',rawcookies)[0]
        cookies = {'li_at':li_at, 'JSESSIONID':f'"{jsessionid[1]}"'}
        headers = {
            'csrf-token': jsessionid[1],
            'x-restli-protocol-version': '2.0.0'
            }
    except Exception as e:
        cookies = None
        logging.error(e, exc_info=True)

    def start_requests(self):
        for url in self.start_urls:
            request = scrapy.Request(
                url = url,
                cookies = {'li_at': self.li_at},
                callback = self.call_api_url
            )
            yield request
    
    def call_api_url(self, response):
        codes_in_json = []
        codes = response.xpath('//code/text()').getall() # get list of all the <codes> and load as list of json
        codes = [c for c in codes if '/voyager/api/organization/companies' in json.dumps(c)]
        for c in codes:
            try:
                c = json.loads(c)
                codes_in_json.append(c)
            except:
                pass
        
        if not codes_in_json:
            logging.error("Couldn't decode the json object sent by LinkedIn")
            return

        code = codes_in_json[0]

        url = "https://www.linkedin.com" + code['request']
        
        # 'x-li-uuid' from response to headers along with csrf obtained from cookies
        headers = code['headers']
        
        # jsessionid = re.findall(b'JSESSIONID\=(ajax\:\d+)', new_cookies)
        try:
            jsessionid = self.jsessionid[1].replace('"','')
            headers['csrf-token'] = jsessionid
        except:
            logging.error("Couldn't find JSESSIONID from cookies")
            return
        

        request = scrapy.Request(
            url = url, 
            headers = headers,
            cookies = {
                'li_at':self.li_at, 
                'JSESSIONID': f'"{jsessionid}"'
            },
            meta = {'url':response.url},
            callback = self.parse                
        )

        yield request

  
    def parse(self, response):

        elements = response.json()['elements'][0]

        # parse linkedin urls
        old_linkedin_url = response.meta['url']
        new_linkedin_url = elements.get('url')
        company_website = elements.get('companyPageUrl')
        if not company_website:
            company_website = elements.get('callToAction')
            if company_website:
               company_website = company_website.get('url') 

        # parse company data
        company_name = elements.get('name')
        
        company_phone = elements.get('phone')
        if company_phone:
            company_phone = company_phone.get('number')
        
        try:
            staffCountRange = elements.get('staffCountRange')
            company_size_start = staffCountRange.get('start')
            company_size_end = staffCountRange.get('end')
            company_size = f'{company_size_start}- {company_size_end} employees'
            if not company_size_end:
                company_size = '10,000+ employees'
        except:
            company_size = ''
        
        employees_on_linkedIn = f'{elements.get("staffCount")} on LinkedIn'
        company_description = elements.get('description')
        
        headquarter = elements.get('headquarter')
        if not headquarter:
            line1, line2, city, geographicArea, postalCode, country, headquarter, address = '', '', '', '', '', '', '', []
        else:
            line1 = headquarter.get('line1')
            line2 = headquarter.get('line2')
            city = headquarter.get('city')
            geographicArea = headquarter.get('geographicArea')
            postalCode = headquarter.get('postalCode')
            country = headquarter.get('country')
            headquarter = f'{city}, {geographicArea}'
            address = [line1, line2, city, geographicArea, postalCode, country]
            address = [c for c in address if c]
        
        foundedOn = elements.get('foundedOn')
        if foundedOn:
            company_founded = foundedOn.get('year')
        else:
            company_founded = ''

        company_specialities = elements.get("specialities")
        if company_specialities:
            company_specialities = ", ".join(company_specialities)
        else:
            company_specialities = ''

        company_type = elements.get('companyType')
        if company_type:
            company_type = company_type.get('localizedName')
        
        company_location_primary = ", ".join(address)
        
        industry = elements.get('companyIndustries')
        if industry:
            industry = [c.get('localizedName') for c in industry]
            industry = [c for c in industry if c]
            industry = ", ".join(industry)

        item = {
            'old_linkedin_url' : old_linkedin_url,
            'new_linkedin_url' : new_linkedin_url,
            'company_website' : company_website,
            'company_name' : company_name,
            'company_phone' : company_phone,
            'company_size' : company_size,
            'employees_on_linkedIn' : employees_on_linkedIn,
            'company_description' : company_description,
            'line1' : line1,
            'line2' : line2,
            'city' : city,
            'geographicArea' : geographicArea,
            'postalCode' : postalCode,
            'country' : country,
            'headquarter' : headquarter,
            'company_founded' : company_founded,
            'company_specialities' : company_specialities,
            'company_type' : company_type,
            'company_location_primary' : company_location_primary,
            'industry' : industry
        }
        
        yield item
