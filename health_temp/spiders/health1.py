# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from bs4 import BeautifulSoup
from health_temp.items import HealthTempItem
import logging
import re

class Health1Spider(scrapy.Spider):
    name = "health1"
    allowed_domains = ["inspire.com"]
    start_urls = (
        'https://www.inspire.com/signin.pl/',
    )

    def parse(self, response):
        return [scrapy.FormRequest.from_response(response,formdata={"email":"pip99tom@yahoo.com",
                    'pw':"aleluya11"},
                     callback=self.after_login)]                   

    def after_login(self,response):
        urls = ['https://www.inspire.com/groups/advanced-breast-cancer/new/active/?page=%s' % page for page in xrange(1,594)]
        for link in urls:
            yield Request(link,callback=self.parse_list)

    def parse_list(self,response):
        links = response.xpath("id('search-results')/h3/a/@href").extract()
        for link in links:
            yield Request(link,callback=self.parse_posts)

    def parse_posts(self, response):
        
        """from scrapy.shell import inspect_response
        inspect_response(response, self)"""
        soup = BeautifulSoup(response.body)
        posts = soup.find('div',{'class':'content-primary-post'})
        posts = [x for x in posts.findAll('ul')]
        posteos = []
        for post in posts:
            if re.findall('By.*', post.li.text) != []:
		posteos.append( re.findall('By.*', post.li.text))
	principal = soup.find('div',{'class':'post-body'}).text.replace("\n"," ").replace("\r"," ")
	secundarios = [com.p for com in soup.findAll('div',{'id':re.compile('cmnt.*')})]
	totales = []
	totales.append(principal)
	for x in secundarios:
            totales.append(x.text.replace("\n"," ").replace("\r"," "))
        items = []
        date =[]
        dates =  soup.findAll('li',{'class':'by'})
        for d in dates:
            if re.findall('\w* \d.*, \d*',d.text) != []:
		date.append(re.findall('\w* \d.*, \d*', d.text))
	authors = []
	href = [x.find('a')['href'] for x in soup.findAll('li',{'class':'by'}) if x.find('a') is not None]
	for x in href:
            if "member" in x:
		authors.append(x)
        topic = soup.find('h1').text
        url = response.url
        for x in range(len(posteos)):
            item=HealthTempItem()
            item['author'] = posteos[x]
            item['author_link']=authors[x]
            item['create_date']= date[x]
            item['post'] = totales[x]
            item['tag']='Advanced Breast Cancer'
            item['topic'] = topic
            item['url']=url
            logging.info(item.__str__)
            items.append(item)
        return items   
