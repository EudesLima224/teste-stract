import requests

API_URL = "https://sidebar.stract.to/api"
TOKEN = "ProcessoSeletivoStract2025"

headers = {"authorization": f"Bearer {TOKEN}"}

response = requests.get(f"{API_URL}/insights?platform=meta_ads&account=1&token=cf76cf576fc567fc56fc5c6f5cf67fc6&fields=adName,impressions,cost,region,clicks,status", headers=headers)

print(response.text)
