import requests

API_URL = "https://sidebar.stract.to/api"
TOKEN = "ProcessoSeletivoStract2025"

# Dados de teste
platform = "meta_ads"  # Ou outra plataforma (meta_ads, tiktok_insights)
account_id = "1"  # Nome da conta, conforme mostrado no print
account_token = "cf76cf576fc567fc56fc5c6f5cf67fc6"  # Token da conta, substitua pelo real
fields = "adName,impressions,clicks,spend,cost"  # Exemplo de campos desejados

headers = {"authorization": f"Bearer {TOKEN}"}

# URL da API de insights
response = requests.get(f"{API_URL}/insights?platform={platform}&account={account_id}&token={account_token}&fields={fields}", headers=headers)


# Verificando o retorno
if response.status_code == 200:
    data = response.json()
    print("Dados de insights:", data)
else:
    print(f"Erro na requisição: {response.status_code}, {response.text}")
