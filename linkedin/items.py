# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LinkedinItem(scrapy.Item):
   
    # parse linkedin urls
    old_linkedin_url = scrapy.Field()
    new_linkedin_url = scrapy.Field()
    company_website = scrapy.Field()

    # parse company data
    company_name = scrapy.Field()
    company_phone = scrapy.Field()
    company_size = scrapy.Field()
    employees_on_linkedIn = scrapy.Field()
    company_description = scrapy.Field()
    line1 = scrapy.Field()
    line2 = scrapy.Field()
    city = scrapy.Field()
    geographicArea = scrapy.Field()
    postalCode = scrapy.Field()
    country = scrapy.Field()
    headquarter = scrapy.Field()
    company_founded = scrapy.Field()
    company_specialities = scrapy.Field()
    company_type = scrapy.Field()
    company_location_primary = scrapy.Field()
    industry = scrapy.Field()
