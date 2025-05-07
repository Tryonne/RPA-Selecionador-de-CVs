import requests
from bs4 import BeautifulSoup
import json

# URL da vaga de trabalho
url = 'https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4224505564'

# Cabeçalhos para simular um navegador
headers = {
    'User-Agent': 'Mozilla/5.0'
}

# Faz a requisição
response = requests.get(url, headers=headers)

# Verifica se a requisição foi bem-sucedida
print(response)  # Deve mostrar <Response [200]>

# Parse do HTML
soup = BeautifulSoup(response.content, 'html.parser')
print(soup.prettify())  # Mostra o HTML formatado

# Função para extrair informações (exemplo genérico)
def extrair_dados(soup):
    empresa = soup.find('div', class_='nome-da-empresa')  # Ajuste para seletor real
    competencias = soup.find_all('span', class_='competencia')  # Ajuste para seletor real

    nome_empresa = empresa.text.strip() if empresa else "Desconhecida"
    lista_competencias = [comp.text.strip() for comp in competencias]

    return {
        "empresa": nome_empresa,
        "competencias": lista_competencias
    }

# Extrai os dados
dados_vaga = extrair_dados(soup)

# Atualiza o ficheiro JSON
ficheiro_json = 'vagas.json'

try:
    with open(ficheiro_json, 'r', encoding='utf-8') as f:
        vagas = json.load(f)
except FileNotFoundError:
    vagas = []

vagas.append(dados_vaga)

with open(ficheiro_json, 'w', encoding='utf-8') as f:
    json.dump(vagas, f, ensure_ascii=False, indent=2)

print("✅ Dados salvos com sucesso.")
