from flask import Flask, Response, request
import requests
import csv
import io

app = Flask(__name__)

# Configurações da API Stract
API_URL = "https://sidebar.stract.to/api"
TOKEN = "ProcessoSeletivoStract2025"

# -------------------------------------------------------------------------
# Funções Auxiliares para Consumir a API
# -------------------------------------------------------------------------

def get_platforms():
    headers = {"Authorization": f"Bearer {TOKEN}"}
    resp = requests.get(f"{API_URL}/platforms", headers=headers)
    if resp.status_code == 200:
        platforms = resp.json()
        return platforms.get("platforms", [])
    else:
        return []

def get_accounts(platform_value):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    resp = requests.get(f"{API_URL}/accounts?platform={platform_value}", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        return data.get("accounts", [])
    else:
        return []

def get_fields(platform_value):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    resp = requests.get(f"{API_URL}/fields?platform={platform_value}", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        return data.get("fields", [])
    else:
        return []

def get_insights(platform_value, account_id, account_token, fields_list):
    fields_str = ",".join(fields_list)
    headers = {"Authorization": f"Bearer {TOKEN}"}
    url = f"{API_URL}/insights?platform={platform_value}&account={account_id}&token={account_token}&fields={fields_str}"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json().get("insights", [])
    else:
        return []

def generate_csv(data, headers_csv):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers_csv)
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()

# -------------------------------------------------------------------------
# Endpoints do Servidor Flask
# -------------------------------------------------------------------------

@app.route('/')
def root():
    info = {
        "nome": "Eudes Moraes Lima",
        "email": "eudeslima2003@gmail.com",
        "linkedin": "https://www.linkedin.com/in/eudes-lima-621457248/"
    }
    return info

@app.route('/<platform>', methods=['GET'])
def platform_report(platform):
    valid_platforms = [p["value"] for p in get_platforms()]
    if platform not in valid_platforms:
        return f"Plataforma '{platform}' inválida.", 400

    accounts = get_accounts(platform)
    fields = get_fields(platform)
    fields_values = [f["value"] for f in fields]

    registros = []
    for account in accounts:
        account_id = account["id"]
        account_name = account["name"]
        account_token = account.get("token", "")  # Obtém o token da conta se disponível
        insights = get_insights(platform, account_id, account_token, fields_values)
        for insight in insights:
            registro = {"Platform": platform, "Account": account_name}
            for f in fields_values:
                registro[f.capitalize()] = insight.get(f, "")
            registros.append(registro)

    headers_csv = ["Platform", "Account"] + [f.capitalize() for f in fields_values]
    csv_data = generate_csv(registros, headers_csv)
    return Response(csv_data, mimetype="text/csv")

@app.route('/<platform>/resumo', methods=['GET'])
def platform_summary(platform):
    valid_platforms = [p["value"] for p in get_platforms()]
    if platform not in valid_platforms:
        return f"Plataforma '{platform}' inválida.", 400

    accounts = get_accounts(platform)
    fields = get_fields(platform)
    fields_values = [f["value"] for f in fields]

    resumo_por_conta = {}
    for account in accounts:
        account_id = account["id"]
        account_name = account["name"]
        account_token = account.get("token", "")
        insights = get_insights(platform, account_id, account_token, fields_values)
        resumo = {"Platform": platform, "Account": account_name}
        for f in fields_values:
            resumo[f.capitalize()] = 0
        for insight in insights:
            for f in fields_values:
                try:
                    resumo[f.capitalize()] += float(insight.get(f, 0))
                except ValueError:
                    resumo[f.capitalize()] = ""
        resumo_por_conta[account_id] = resumo

    registros = list(resumo_por_conta.values())
    headers_csv = ["Platform", "Account"] + [f.capitalize() for f in fields_values]
    csv_data = generate_csv(registros, headers_csv)
    return Response(csv_data, mimetype="text/csv")

@app.route('/geral', methods=['GET'])
def geral_report():
    platforms = get_platforms()
    registros = []
    campos_unicos = set()

    for platform in platforms:
        platform_value = platform["value"]
        accounts = get_accounts(platform_value)
        fields = get_fields(platform_value)
        fields_values = [f["value"] for f in fields]
        campos_unicos.update(fields_values)
        for account in accounts:
            account_id = account["id"]
            account_name = account["name"]
            account_token = account.get("token", "")
            insights = get_insights(platform_value, account_id, account_token, fields_values)
            for insight in insights:
                registro = {"Platform": platform_value, "Account": account_name}
                for campo in campos_unicos:
                    registro[campo.capitalize()] = insight.get(campo, "")
                if platform_value == "ga4":
                    try:
                        clicks = float(insight.get("clicks", 0))
                        spend = float(insight.get("cost", 0))
                        registro["Cost per Click"] = spend / clicks if clicks > 0 else 0
                    except ValueError:
                        registro["Cost per Click"] = ""
                registros.append(registro)

    headers_csv = ["Platform", "Account"] + sorted([campo.capitalize() for campo in campos_unicos])
    csv_data = generate_csv(registros, headers_csv)
    return Response(csv_data, mimetype="text/csv")

@app.route('/platforms', methods=['GET'])
def listar_plataformas():
    """
    Endpoint para listar todas as plataformas disponíveis.
    """
    platforms = get_platforms()
    return {"platforms": platforms}, 200


@app.route('/geral/resumo', methods=['GET'])
def geral_summary():
    platforms = get_platforms()
    resumo_por_plataforma = {}
    campos_unicos = set()

    for platform in platforms:
        platform_value = platform["value"]
        accounts = get_accounts(platform_value)
        fields = get_fields(platform_value)
        fields_values = [f["value"] for f in fields]
        campos_unicos.update(fields_values)
        for account in accounts:
            account_id = account["id"]
            account_token = account.get("token", "")
            insights = get_insights(platform_value, account_id, account_token, fields_values)
            for insight in insights:
                if platform_value not in resumo_por_plataforma:
                    resumo = {"Platform": platform_value}
                    for campo in fields_values:
                        resumo[campo.capitalize()] = 0
                    resumo_por_plataforma[platform_value] = resumo
                resumo = resumo_por_plataforma[platform_value]
                for campo in fields_values:
                    try:
                        resumo[campo.capitalize()] += float(insight.get(campo, 0))
                    except ValueError:
                        resumo[campo.capitalize()] = ""
                resumo_por_plataforma[platform_value] = resumo

    registros = list(resumo_por_plataforma.values())
    headers_csv = ["Platform"] + sorted([campo.capitalize() for campo in campos_unicos])
    csv_data = generate_csv(registros, headers_csv)
    return Response(csv_data, mimetype="text/csv")

if __name__ == '__main__':
    app.run(debug=True)
