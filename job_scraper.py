import requests
from bs4 import BeautifulSoup
import json

class JobScraper:
    def __init__(self):
        self.base_url = "https://expressoemprego.pt/emprego/pesquisa"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def search_jobs(self, department):
        jobs = []
        try:
            # Format department name for URL
            formatted_department = department.lower().replace(' ', '-')
            url = f"{self.base_url}/{formatted_department}"
            
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            job_listings = soup.find_all('div', class_='resultadosBox')
            
            for job in job_listings:
                # Get title and link
                title_elem = job.find('h3', class_='fOpenSansSemiBold').find('a')
                if title_elem:
                    title = title_elem.text.strip()
                    link = title_elem.get('href')
                else:
                    title = "N/A"
                    link = ""
                
                # Get company
                company = job.find('h4', class_='fOpenSansSemiBold')
                company = company.text.strip() if company else "N/A"
                
                # Get location and date
                info_text = job.find('span', class_='px13 colorBlack')
                location = "N/A"
                if info_text:
                    location = info_text.text.split('|')[1].strip() if '|' in info_text.text else "N/A"
                
                # Get description
                description = job.find('div', class_='px13 colorGray8 hidden-xs')
                description = description.text.strip() if description else "N/A"
                
                jobs.append({
                    'title': title,
                    'company': company,
                    'location': location,
                    'description': description,
                    'link': link  # Now storing just the relative URL
                })
            
            return jobs, len(jobs)
        except Exception as e:
            print(f"Error scraping jobs: {str(e)}")
            return [], 0