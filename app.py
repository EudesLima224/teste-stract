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
        return resp.json().get("platforms", [])
    return []

def get_accounts(platform_value):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    resp = requests.get(f"{API_URL}/accounts?platform={platform_value}", headers=headers)
    if resp.status_code == 200:
        return resp.json().get("accounts", [])
    return []

def get_fields(platform_value):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    resp = requests.get(f"{API_URL}/fields?platform={platform_value}", headers=headers)
    if resp.status_code == 200:
        return resp.json().get("fields", [])
    return []

def get_insights(platform_value, account_id, account_token, fields_list):
    fields_str = ",".join(fields_list)
    headers = {"Authorization": f"Bearer {TOKEN}"}
    url = f"{API_URL}/insights?platform={platform_value}&account={account_id}&token={account_token}&fields={fields_str}"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json().get("insights", [])
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
                if platform_value == 'meta_ads':
                    for campo in campos_unicos:
                        if campo.capitalize() == 'Cpc':
                            campo2 = 'Cost_per_click'
                            valor = insight.get(campo, "")
                            if valor:  # Adiciona apenas se não for vazio
                                registro[campo2.capitalize()] = valor
                        else:
                            registro[campo.capitalize()] = insight.get(campo, "")

                else:
                    for campo in campos_unicos:
                        registro[campo.capitalize()] = insight.get(campo, "")

                # Adiciona "Cost per Click" para GA4
                if platform_value == "ga4":
                    try:
                        clicks = float(insight.get("clicks", 0))
                        spend = float(insight.get("cost", 0))
                        registro["Cost_per_click"] = round(spend / clicks, 2) if clicks > 0 else 0
                    except ValueError:
                        registro["Cost_per_click"] = ""

                    for campo in campos_unicos:
                        if campo.capitalize() == 'Region':
                            campo2 = 'Country'
                            valor = insight.get(campo, "")
                            if valor:  # Adiciona apenas se não for vazio
                                registro[campo2.capitalize()] = valor
                        else:
                            registro[campo.capitalize()] = insight.get(campo, "")

                # Exclui a chave "Cpc" se ela estiver vazia
                if "Cpc" in registro and not registro["Cpc"]:
                    del registro["Cpc"]
                
                # Transfere o conteúdo de 'region' para 'country' e apaga 'region'
                if "region" in registro and registro["region"]:
                    registro["country"] = registro["region"]
                    del registro["region"]
                    
                registros.append(registro)

    # Garante que "Cpc" (ou "Cost_per_click") não seja adicionada aos headers caso não exista
    headers_csv = ["Platform", "Account"] + sorted([campo.capitalize() for campo in campos_unicos])
    
    # Remove a coluna "Cpc" de headers_csv se ela não for utilizada
    if "Cpc" in headers_csv:
        headers_csv.remove("Cpc")
    
    if "Cost_per_click" not in headers_csv and any("Cost_per_click" in r for r in registros):
        headers_csv.append("Cost_per_click")

    csv_data = generate_csv(registros, headers_csv)

    filename = "geral.csv"
    response = Response(csv_data, mimetype="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


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
                    resumo["Cost_per_click"] = 0  # Inicializa Cost_per_click
                    resumo_por_plataforma[platform_value] = resumo
                resumo = resumo_por_plataforma[platform_value]
                
                # Lógica para o cálculo de Cost_per_click
                if platform_value == "meta_ads":
                    # Para a plataforma meta_ads, soma-se o Cpc
                    cpc = insight.get("cpc")
                    if cpc:
                        try:
                            cpc_value = float(cpc)
                            if cpc_value < 0 or cpc_value > 1000000:  # Limitar os valores absurdos, ajustando conforme necessário
                                print(f"Valor de Cpc muito grande ou negativo: {cpc_value}")
                            else:
                                resumo["Cost_per_click"] = round(resumo.get("Cost_per_click", 0) + cpc_value, 2)
                        except ValueError:
                            print(f"Valor de Cpc inválido para o insight: {cpc}")
                    else:
                        print("Cpc não encontrado ou vazio para este insight.")



                else:
                    # Para as demais plataformas, calcula-se Cost_per_click como Cost dividido por Clicks
                    try:
                        clicks = float(insight.get("clicks", 0))
                        spend = float(insight.get("cost", 0))
                        if clicks > 0:
                            resumo["Cost_per_click"] = round(spend / clicks, 2)
                        else:
                            resumo["Cost_per_click"] = 0
                    except ValueError:
                        resumo["Cost_per_click"] = ""

                # Preenche os outros campos, mas não soma o 'cost'
                for campo in fields_values:
                    try:
                        # Evitar somar 'cost' nos outros campos
                        if campo != "cost":
                            resumo[campo.capitalize()] += float(insight.get(campo, 0))
                        else:
                            # A soma do 'cost' deve ser feita de maneira separada
                            spend = float(insight.get("cost", 0))
                            resumo["Cost"] = round(resumo.get("Cost", 0) + spend, 2)
                    except ValueError:
                        resumo[campo.capitalize()] = ""


    registros = list(resumo_por_plataforma.values())

    # Ajuste aqui para remover "Cpc" na rota /geral/resumo
    headers_csv = ["Platform"] + sorted([campo.capitalize() for campo in campos_unicos])
    
    # Remover "Cpc" dos registros
    for registro in registros:
        if "Cpc" in registro:
            del registro["Cpc"]

    # Se "Cpc" estiver nos headers, remova
    if "Cpc" in headers_csv:
        headers_csv.remove("Cpc")
    
    csv_data = generate_csv(registros, headers_csv)

    filename = "geral-resumo.csv"
    response = Response(csv_data, mimetype="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response



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

    filename = f"{platform}-resumo.csv"
    response = Response(csv_data, mimetype="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


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
        account_token = account.get("token", "")
        insights = get_insights(platform, account_id, account_token, fields_values)
        
        for insight in insights:
            registro = {"Platform": platform, "Account": account_name}
            for f in fields_values:
                registro[f.capitalize()] = insight.get(f, "")
            
            registros.append(registro)

    headers_csv = ["Platform", "Account"] + [f.capitalize() for f in fields_values]
    csv_data = generate_csv(registros, headers_csv)

    filename = f"{platform}.csv"
    response = Response(csv_data, mimetype="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


if __name__ == '__main__':
    app.run(debug=True)
