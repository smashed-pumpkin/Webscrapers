# -*- coding: utf-8 -*-'
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import glob
import re

def locate(filename):   
    print('Searching...')
    cwd = os.getcwd()
    os.chdir('C:\\')
    for f in glob.iglob('**/'+filename, recursive=True):
        path = f
    os.chdir(cwd)
    print('Found!')
    return(path)

# Open ChromeDriver:
driver = webdriver.Chrome(locate("chromedriver.exe"))


## Define a Wages class: 
class Wages:
    def __init__(self, 
                 Country, 
                 Link = None,
                 Currency = None, 
                 PerMonth = None, 
                 PerHour = None,
                 LastUpdated = None
                 ):
        self.Country=Country
        self.Link=Link
        self.Currency=Currency
        self.PerMonth=PerMonth
        self.PerHour=PerHour
        self.LastUpdated=LastUpdated
    def setattrs(_self, **kwargs):
        for k,v in kwargs.items():
            setattr(_self, k, v)    
    def to_dict(self):
        return { 'Link': self.Link,
                 'Country': self.Country,
                 'Currency': self.Currency,
                 'PerMonth': self.PerMonth,
                 'PerHour': self.PerHour,
                 'LastUpdated': self.LastUpdated
                 }


## Get the list of countries:
url = 'https://wageindicator.org/salary/minimum-wage' 
driver.get(url)

country_elem1 = driver.find_elements_by_xpath('//*[@id="visual-portal-wrapper"]/div[1]/main/main/article/div/table/tbody/tr/td/strong')
country_elem2 = driver.find_elements_by_xpath('//*[@id="visual-portal-wrapper"]/div[1]/main/main/article/div/table/tbody/tr/td/p/strong')
country_elem3 = driver.find_elements_by_xpath('//*[@id="visual-portal-wrapper"]/div[1]/main/main/article/div/table/tbody/tr/td/div/strong')

list_data = []
for array in [country_elem1, country_elem2, country_elem3]:
	for e in array:
		country_name = e.text.strip().replace('é','e')
		list_data.append(Wages(Country = country_name, Link = url+"/"+country_name.replace(' ','-').lower()))
		print('Added', country_name, url+"/"+country_name.replace(' ','-').lower())


## Collect data for each country:
for i in list_data:
	try:
		driver.get(i.Link)
		time.sleep(3)	
		curr_elem = driver.find_elements_by_xpath('//*[@id="content"]/ul/li')
		for e in curr_elem:
		    if 'Valid on' in e.text:
		        LastUpdated = e.text
		        i.setattrs(LastUpdated = LastUpdated)
		    elif 'The amounts are in' in e.text:
		       	Currency = e.text.replace('The amounts are in ', '').replace('.','')
		       	i.setattrs(Currency = Currency)
		try:
			wage_elem = driver.find_elements_by_class_name('amount')
			rows = len(driver.find_elements_by_xpath('//*[@id="content"]/article/div/table/tbody/tr'))
			columns = len(driver.find_elements_by_xpath('//*[@id="content"]/article/div/table/tbody/tr[1]/td'))
			for c,v in enumerate(wage_elem):
				if 'Hour' in v.text:
					i.setattrs(PerHour = wage_elem[c+columns-1].text)
				elif 'Month' in v.text:
					i.setattrs(PerMonth = wage_elem[c+columns-1].text)
		except:
			print('No wage data collected for', i.Country)
			pass
		print('Done with', i.Country)
	except:
		print("Error with", l.Link)
		pass


## Aggregate all:
import pandas as pd
import datetime
import os

df = pd.DataFrame([s.to_dict() for s in list_data])
df = df.drop_duplicates()
df['Date of scrape'] = datetime.datetime.today().strftime('%Y-%m-%d %H:%M')

file_name = locate('MinWages_Worldwide.py').replace('.py','.csv')
df.to_csv(file_name, sep=',', encoding='utf-8-sig')
os.startfile(file_name)

