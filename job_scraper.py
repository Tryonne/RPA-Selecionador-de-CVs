from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import json
import time

options = Options()
options.add_argument('--headless')  # executa sem abrir janela

driver = webdriver.Firefox(options=options)

url = 'https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4223895272'
driver.get(url)
time.sleep(5)  # esperar JS carregar

soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

# Extração simulada
vaga = soup.find('h1')
empresa = soup.find('a', class_='topcard__org-name-link') or soup.find('span', class_='topcard__flavor')
competencias = ['Middleware', 'TIBCO BusinessWorks']  # adaptar ao conteúdo real

vaga_info = {
    "empresa": empresa.text.strip() if empresa else "Desconhecida",
    "competencias": competencias
}

with open('vagas.json', 'w', encoding='utf-8') as f:
    json.dump([vaga_info], f, indent=2, ensure_ascii=False)

print("✅ Dados extraídos com sucesso.")
