import requests

# A URL base da API
base_url = "https://sidebar.stract.to/api"

# Token de autorização (substitua pelo token recebido)
token = "ProcessoSeletivoStract2025"

# Função para buscar insights para uma plataforma e conta específicas
def fetch_insights(platform, account):
    # Monta a URL com os parâmetros necessários para a requisição
    url = f"{base_url}/api/insights?platform={platform}&account={account}&token={token}&fields=clicks,impressions,spend,cpc,ctr"
    
    # Faz a requisição GET à API e armazena a resposta
    response = requests.get(url)
    
    # Verifica se a requisição foi bem-sucedida (status code 200)
    if response.status_code == 200:
        return response.json()  # Retorna os dados da resposta em formato JSON
    else:
        print(f"Erro ao buscar insights para a plataforma {platform} e conta {account}: {response.status_code}")
        return None

# Exemplo de uso da função fetch_insights
platform = "meta_ads"  # Facebook Ads
account = "1"  # ID da conta (ex: Jorginho)

insights = fetch_insights(platform, account)
if insights:
    print(insights)  # Exibe os insights no console
