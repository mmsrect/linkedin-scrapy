# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import csv
import logging
from os.path import exists
from itemadapter import ItemAdapter


class LinkedinPipeline:
    def open_spider(self, spider):    
        if spider.name == 'url_to_company_data':
            self.filename = 'output/company-data.csv'
            header = ['old_linkedin_url', 'new_linkedin_url', 'company_website', 'company_name', 'company_phone', 'company_size', 'employees_on_linkedIn', 'company_description', 'line1', 'line2', 'city', 'geographicArea', 'postalCode', 'country', 'headquarter', 'company_founded', 'company_specialities', 'company_type', 'company_location_primary', 'industry']
            
            file_exists = exists(self.filename)
            if not file_exists:
                with open(self.filename, 'w', encoding='UTF8') as f:
                    writer = csv.writer(f)
                    writer.writerow(header)
        else:
            self.filename = 'output/linkedin-urls.csv'
        
    def process_item(self, item, spider):
        datarow_raw = [item[key] for key in item]
        with open(self.filename, 'a', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(datarow_raw)
        logging.info(item)
        return item
