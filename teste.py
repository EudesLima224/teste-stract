import flask
import requests

API_URL = "https://sidebar.stract.to/api"
TOKEN = "ProcessoSeletivoStract2025"
headers = {"Authorization": f"Bearer {TOKEN}"}

response = requests.get(f'{API_URL}', headers=headers)
print(response.text)