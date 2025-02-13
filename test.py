import requests

# Token de autorização fornecido pela Stract
TOKEN = "ProcessoSeletivoStract2025"

# URL base da API
BASE_URL = "https://sidebar.stract.to/api"

# Fazendo a requisição para obter as plataformas disponíveis
headers = {"Authorization": f"Bearer {TOKEN}"}
response = requests.get(f"{BASE_URL}/platforms", headers=headers)

if response.status_code == 200:
    platforms = response.json()["platforms"]
    print("\n📌 Plataformas disponíveis:")
    for platform in platforms:
        platform_name = platform['text']
        platform_id = platform['value']
        print(f"- {platform_name} ({platform_id})")

        # Fazendo a requisição para obter as contas dessa plataforma
        accounts_url = f"{BASE_URL}/accounts?platform={platform_id}"
        accounts_response = requests.get(accounts_url, headers=headers)

        if accounts_response.status_code == 200:
            accounts_data = accounts_response.json()
            print("  📋 Contas disponíveis:")

            if "accounts" in accounts_data:
                accounts = accounts_data["accounts"]
                for account in accounts:
                    print(f"    - {account['name']} (ID: {account['id']})")
            else:
                print("  ❌ A chave 'accounts' não foi encontrada na resposta!")

        # Fazendo a requisição para obter os campos de insights dessa plataforma
        fields_url = f"{BASE_URL}/fields?platform={platform_id}"
        fields_response = requests.get(fields_url, headers=headers)

        if fields_response.status_code == 200:
            fields_data = fields_response.json()
            print("  📊 Campos de insights disponíveis:")

            if "fields" in fields_data:
                fields = fields_data["fields"]
                for field in fields:
                    print(f"    - {field['text']} ({field['value']})")
            else:
                print("  ❌ Nenhum campo de insights encontrado!")
        else:
            print(f"  ❌ Erro ao buscar campos de insights: {fields_response.status_code}")

else:
    print(f"❌ Erro ao buscar plataformas: {response.status_code}")
