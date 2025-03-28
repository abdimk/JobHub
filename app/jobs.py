import time
import csv
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
from urllib.request import Request, urlopen
import urllib.request
import numpy as np
from jobspy import scrape_jobs
from typing import List, Dict, Optional, Union, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('job_scraper')

class JobScraper:
    """A class for scraping job listings from various job boards."""
    
    def __init__(self, headless: bool = True):
        """
        Initialize the job scraper with browser settings.
        
        Args:
            headless: Whether to run the browser in headless mode
        """
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/92.0.4515.107 Mobile Safari/537.36'
        }
        
        
        self.chrome_options = webdriver.ChromeOptions()
        if headless:
            self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.chrome_options.add_argument(f"user-agent={self.headers['user-agent']}")
        
        
        self.driver = None
        self._initialize_driver()
        
    def _initialize_driver(self):
        """Initialize and configure the Chrome WebDriver with stealth settings."""
        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), 
                options=self.chrome_options
            )
            
            # Apply stealth settings
            stealth(
                self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )
            logger.info("WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def __del__(self):
        """Clean up resources when the object is destroyed."""
        if self.driver:
            self.driver.quit()
    
    def _check_next_page_exists(self, url: str, method: str = "default") -> bool:
        """
        Check if a next page exists for pagination.
        
        Args:
            url: The URL to check
            method: The method to use for checking ("default", "indeed", or "linkedin")
            
        Returns:
            True if next page exists, False otherwise
        """
        try:
            if method == "default":
                req = urllib.request.Request(url, headers=self.headers)
                time.sleep(1)  # Avoid rate limiting
                with urlopen(req) as webUrl:
                    html = webUrl.read()
                soup = BeautifulSoup(html, 'html.parser')
                return not bool(soup.find('div', {'class': 'noResults'}))
                
            elif method in ("indeed", "linkedin"):
                self.driver.get(url)
                html = self.driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                
                if method == "indeed":
                    return bool(soup.find('div', id='mosaic-provider-jobcards'))
                else:  # linkedin
                    return bool(soup.find('li'))
                    
            else:
                logger.warning(f"Unknown method: {method}")
                return False
                
        except Exception as e:
            logger.error(f"Error checking next page: {e}")
            return False
    
    def search_ziprecruiter(self, skill: str, place: str, page: int = 1, max_pages: int = 5) -> List[List[str]]:
        """
        Search for jobs on ZipRecruiter.
        
        Args:
            skill: The job skill to search for
            place: The location to search in
            page: The starting page number
            max_pages: Maximum number of pages to scrape
            
        Returns:
            A list of job listings
        """
        ziprecruiter_list = []
        current_page = page
        
        try:
            while current_page < (page + max_pages):
                url = f"https://www.ziprecruiter.ie/jobs/search?q={skill}&l={place}&page={current_page}"
                logger.info(f"Scraping ZipRecruiter page {current_page}: {url}")
                
                self.driver.get(url)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
                jobs = soup.find_all('li', class_='job-listing')
                if not jobs:
                    logger.info("No more jobs found on ZipRecruiter")
                    break
                    
                for job in jobs:
                    # Job Title
                    title_elem = job.find('a', class_='jobList-title')
                    title = title_elem.text.strip() if title_elem else 'No Title'
                    
                    # Company
                    company_elem = job.find('li', string=lambda t: t and 'fas fa-building' in str(t))
                    company = company_elem.text.strip() if company_elem else 'No Company'
                    
                    # Location
                    location_elem = job.find('li', string=lambda t: t and 'fas fa-map-marker-alt' in str(t))
                    location = location_elem.text.strip() if location_elem else 'No Location'
                    
                    # Post Date
                    date_elem = job.find('div', class_='jobList-date')
                    post_date = date_elem.text.strip() if date_elem else 'No Date'
                    
                    ziprecruiter_list.append([company, title, location, post_date])
                
                current_page += 1
                time.sleep(random.uniform(1.5, 3.0))  # Random delay between requests
                
            logger.info(f"Found {len(ziprecruiter_list)} jobs on ZipRecruiter")
            return ziprecruiter_list
            
        except Exception as e:
            logger.error(f"Error searching ZipRecruiter: {e}")
            return ziprecruiter_list
    
    def search_linkedin(self, skill: str, place: str, page: int = 0, max_pages: int = 5) -> List[List[str]]:
        """
        Search for jobs on LinkedIn.
        
        Args:
            skill: The job skill to search for
            place: The location to search in
            page: The starting page number
            max_pages: Maximum number of pages to scrape
            
        Returns:
            A list of job listings
        """
        linkedin_list = []
        current_page = page
        
        try:
            while current_page < (page + max_pages):
                url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={skill}&location={place}&start={current_page}"
                logger.info(f"Scraping LinkedIn page {current_page}: {url}")
                
                self.driver.get(url)
                html = self.driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                
                list_items = soup.find('body').find_all('li') if soup.find('body') else []
                
                if not list_items:
                    logger.info("No more jobs found on LinkedIn")
                    break
                
                for item in list_items:
                    # Initialize with default values
                    job_data = {
                        'company': 'No Company',
                        'job': 'No Job Title',
                        'link': 'No Link',
                        'salary': 'No Salary',
                        'post_date': 'No Date'
                    }
                    
                    # Job Title
                    job_title = item.find('h3', class_='base-search-card__title')
                    if job_title:
                        job_data['job'] = job_title.get_text(strip=True)
                    
                    # Company Name
                    company_elem = item.find('h4', class_='base-search-card__subtitle')
                    if company_elem:
                        job_data['company'] = company_elem.get_text(strip=True)
                    
                    # Link
                    link_elem = item.find('a', class_='base-card__full-link')
                    if link_elem and link_elem.has_attr('href'):
                        job_data['link'] = link_elem['href']
                    
                    # Salary
                    salary_elem = item.find('div', class_='job-salary')
                    if salary_elem:
                        job_data['salary'] = salary_elem.get_text(strip=True)
                    
                    # Post Date
                    post_date_elem = item.find('time', class_=lambda c: c and ('job-search-card__listdate' in c or 'job-search-card__listdate--new' in c))
                    if post_date_elem:
                        job_data['post_date'] = post_date_elem.get_text(strip=True)
                    
                    linkedin_list.append([
                        job_data['company'], 
                        job_data['job'], 
                        job_data['link'], 
                        job_data['salary'], 
                        job_data['post_date']
                    ])
                
                current_page += 25  # LinkedIn pagination typically uses 25 job increments
                
                # Check if there's a next page
                if not self._check_next_page_exists(url, "linkedin"):
                    break
                    
                time.sleep(random.uniform(1.5, 3.0))  # Random delay between requests
            
            logger.info(f"Found {len(linkedin_list)} jobs on LinkedIn")
            return linkedin_list
            
        except Exception as e:
            logger.error(f"Error searching LinkedIn: {e}")
            return linkedin_list
    
    def search_with_jobspy(self, site_name: List[str], search_term: str, 
                          google_search_term: str, location: str = "newyork",
                          results_wanted: int = 30, hours_old: int = 72,
                          country: str = "usa") -> List[List[str]]:
        """
        Search for jobs using the jobspy library.
        
        Args:
            site_name: List of sites to search (e.g., ["indeed", "google"])
            search_term: The job search term
            google_search_term: The Google search term
            location: Location to search in
            results_wanted: Number of results to return
            hours_old: Maximum age of job postings in hours
            country: Country to search in
            
        Returns:
            A list of job listings
        """
        try:
            logger.info(f"Searching {', '.join(site_name)} using jobspy")
            
            jobs = scrape_jobs(
                site_name=site_name,
                search_term=search_term,
                google_search_term=google_search_term,
                location=location,
                results_wanted=results_wanted,
                hours_old=hours_old,
                country_indeed=country,
            )
            
            total_jobs = len(jobs)
            logger.info(f"Found {total_jobs} jobs using jobspy")
            
            # Save to CSV (optional)
            output_file = f"{site_name[0]}_jobs.csv"
            jobs.to_csv(output_file, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
            
            # Extract needed columns
            columns_needed = ["company", "title", "job_url", "salary_source", "date_posted"]
            
            # Clean the dataframe
            df_cleaned = jobs[columns_needed].applymap(
                lambda x: None if isinstance(x, float) and np.isnan(x) else x
            )
            
            # Convert to list format
            result = df_cleaned.apply(lambda row: [
                row["company"],
                row["title"],
                row["job_url"],
                row["salary_source"] if row["salary_source"] != "None" else "No Salary",
                row["date_posted"]
            ], axis=1).tolist()
            
            return result
            
        except Exception as e:
            logger.error(f"Error using jobspy: {e}")
            return []

# Helper function for random delays
def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
    """Add a random delay to avoid detection."""
    time.sleep(random.uniform(min_seconds, max_seconds))

# Example usage
if __name__ == "__main__":
    import random
    
    # Initialize the scraper
    scraper = JobScraper(headless=True)
    
    # Example: Search for Data Engineer jobs in New York
    skill = "Data Engineer"
    location = "New York"
    
    # LinkedIn search
    linkedin_jobs = scraper.search_linkedin(skill, location, page=0, max_pages=2)
    print(f"Found {len(linkedin_jobs)} jobs on LinkedIn")
    
    # ZipRecruiter search
    ziprecruiter_jobs = scraper.search_ziprecruiter(skill, location, page=1, max_pages=2)
    print(f"Found {len(ziprecruiter_jobs)} jobs on ZipRecruiter")
    
    
    indeed_jobs = scraper.search_with_jobspy(
        site_name=["indeed", "google"],
        search_term="Data Engineer",
        google_search_term="Data Engineer near New York",
        location="New York",
        results_wanted=30
    )
    print(f"Found {len(indeed_jobs)} jobs on Indeed via JobSpy")
    
    
    del scraper
