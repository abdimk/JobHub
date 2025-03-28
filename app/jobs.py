import time
import re
import random
import csv
import pandas as pd
import bs4
import numpy as np
from collections import defaultdict
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import undetected_chromedriver as uc
from urllib.request import Request, urlopen
from datetime import datetime
from selenium_stealth import stealth
from jobspy import scrape_jobs
from webdriver_manager.chrome import ChromeDriverManager




indeed_posts=[]

headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Mobile Safari/537.36'}

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument(f"user-agent={headers}")


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

# a function to check if there is a website in next page
def isThereSite(url:str | None)->bool:
        headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Mobile Safari/537.36'}
        req = urllib.request.Request(url,headers=headers)
        #to advoid sending too many requests at one time
        time.sleep(1)
        webUrl = urlopen(req)
        html=webUrl.read()
        # Scrapping the Web
        soup = BeautifulSoup(html, 'html.parser')
       
        # Outer Most Entry Point of HTML:
        if soup.find('div',{'class':'noResults'}) :
                return False
        return True

def isThereASiteIndeed(url:str | None)->bool:
              
                driver.get(url)
                html=driver.page_source
                # Scrapping the Web (you can use 'html' or 'lxml')
                soup = BeautifulSoup(html, 'html.parser')
            
                # Outer Most Entry Point of HTML:
                if soup.find('div',id='mosaic-provider-jobcards'):
                    return True
                return False

def isThereASiteLinkdin(url:str | None)->bool:
               
                driver.get(url)
                html=driver.page_source
                # Scrapping the Web (you can use 'html' or 'lxml')
                soup = BeautifulSoup(html, 'html.parser')
            
                # Outer Most Entry Point of HTML:
                if soup.find('li'):
                    return True
                return False


def searchJobsZipRecruiter(skill:str | None, place:str | None, page:int | None)->list[list[str]]:
     
    headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Mobile Safari/537.36'}

    maxPage=page+50
    indeedList=[]
    nextPage=True
        #printing the current skill we are looking for
        #a loop which ends when there are no next page 
    # ... (headers and setup similar to LinkedIn function)
    
    ziprecruiter_list = []
    url = f"https://www.ziprecruiter.ie/jobs/search?q={skill}&l={place}&page={page}"
    
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    for job in soup.find_all('li', class_='job-listing'):
        # Job Title
        title_elem = job.find('a', class_='jobList-title')
        title = title_elem.text.strip() if title_elem else 'No Title'
        
        # Company
        company_elem = job.find('li', string=lambda t: t and 'fas fa-building' in str(t))
        company = company_elem.text.strip() if company_elem else 'No Company'
        
        # Location
        location_elem = job.find('li', string=lambda t: t and 'fas fa-map-marker-alt' in str(t))
        location = location_elem.text.strip() if location_elem else 'No Location'
        
        # Post Date - Key Extraction
        date_elem = job.find('div', class_='jobList-date')
        post_date = date_elem.text.strip() if date_elem else 'No Date'
        
        ziprecruiter_list.append([company, title, location, post_date])
    
    return ziprecruiter_list


def searchJobsLinkdin(skill:str | None,place:str | None ,page:str | None) -> list[list[str]]:
    # this was used for the person contacting me who had these details for their system
    headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Mobile Safari/537.36'}

   
    linkdinlist=[]
    nextPage=True
    maxPage=page+5
        #printing the current skill we are looking for
        #a loop which ends when there are no next page 
    while nextPage:      
                if page==maxPage:
                        break
                url =" https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords="+skill+"&location="+place+"&start="+str(page)
                print(url)
              
                driver.get(url)
                html=driver.page_source
                
                soup = BeautifulSoup(html, 'html.parser')
            
                
                outer_most_point=soup.find('body')
            
                # "UL" lists where the data are stored:
                company=[]
                jobs=[]
                links=[]
                salary=[]
                post_date=[]
                if outer_most_point is not None and isinstance(outer_most_point, bs4.element.Tag):
                        list_items = outer_most_point.find_all('li')


                for i in list_items:
                        # Initialize variables for each job
                        company = 'No Company'
                        job = 'No Job Title'
                        link = 'No Link'
                        salary = 'No Salary'
                        post_date = 'No Date'

                        # Job Title
                        job_title = i.find('h3', class_='base-search-card__title')
                        if job_title:
                                job = job_title.get_text(strip=True)

                        # Company Name
                        company_elem = i.find('h4', class_='base-search-card__subtitle')
                        if company_elem:
                                company = company_elem.get_text(strip=True)

                        # Link
                        link_elem = i.find('a', class_='base-card__full-link')
                        if link_elem and link_elem.has_attr('href'):
                                link = link_elem['href']

                        # Salary (adjust selector if needed for LinkedIn)
                        salary_elem = i.find('div', class_='job-salary')  # Update class based on actual structure
                        if salary_elem:
                                salary = salary_elem.get_text(strip=True)

                        # Post Date - Corrected Part
                        post_date_elem = i.find('time', class_=lambda c: c and ('job-search-card__listdate' in c or 'job-search-card__listdate--new' in c))
                        if post_date_elem:
                                post_date = post_date_elem.get_text(strip=True)

                        linkdinlist.append([company, job, link, salary, post_date])
                page=page+1
                  
                nextPage=isThereASiteLinkdin(url)
    return linkdinlist

def searchOnIndeed(search_term: str, google_search_term:str):
    
    jobs = scrape_jobs(
        site_name=["indeed", "google"],
        search_term=f"Data engineer",
        google_search_term=f"Data engineer near newyork",
        location="newyork",
        results_wanted=30,
        hours_old=72,
        country_indeed="usa",
    )

    total_Jobs = len(jobs)
    jobs.to_csv("jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)  # Save to CSV
    
    df = pd.read_csv('jobs.csv')
    
    columns_needed = ["company", "title", "job_url", "salary_source", "date_posted"]
    
    df_cleaned = df[columns_needed].applymap(lambda x: None if isinstance(x, float) and np.isnan(x) else x)

    result = df_cleaned.apply(lambda row: [
        row["company"],
        row["title"],
        row["job_url"],
        row["salary_source"] if row["salary_source"] != "None" else "No Salary",
        row["date_posted"]
    ], axis=1).tolist()

    return result




# do ziprecruiter
def ziprecruiter(search_term: str, google_search_term:str):
        jobs = scrape_jobs(
                site_name=["zip_recruiter", "google"],
                search_term=f"Data engineer",
                google_search_term=f"Data engineer near newyork",
                location="newyork",
                results_wanted=30,
                hours_old=72,
                country_indeed="usa",
                )
        

        total_Jobs = len(jobs)
        jobs.to_csv("jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)  # Save to CSV

        
        df = pd.read_csv('zipr.csv')

        
        columns_needed = ["company", "title", "job_url", "salary_source", "date_posted"]

        
        df_cleaned = df[columns_needed].applymap(lambda x: None if isinstance(x, float) and np.isnan(x) else x)

        
        result = df_cleaned.apply(lambda row: [
                row["company"],
                row["title"],
                row["job_url"],
                row["salary_source"] if row["salary_source"] != "None" else "No Salary",
                row["date_posted"]
        ], axis=1).tolist()

        return result

        