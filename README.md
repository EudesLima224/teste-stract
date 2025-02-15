
# API de Relatórios de Anúncios - Stract

Esta é uma API desenvolvida como parte de um processo seletivo para a Stract. Ela consome dados de contas de anúncios de diferentes plataformas e gera relatórios em formato CSV.

## Endpoints

### 1. `/`
Retorna minhas informações pessoais (nome, email e LinkedIn).

**Exemplo de resposta:**
```json
{
  "nome": "Seu Nome",
  "email": "seu.email@dominio.com",
  "linkedin": "https://www.linkedin.com/in/seulinkedin"
}
```

### 2. `/{{plataforma}}`
Retorna uma tabela de anúncios veiculados na plataforma especificada. As colunas são baseadas nos campos de insights daquela plataforma.

**Exemplo de resposta:**
```csv
Platform,Ad Name,Clicks,Impressions,Cost
Facebook,Ad 1,100,1000,50
YouTube,Ad 2,150,2000,70
```

### 3. `/{{plataforma}}/resumo`
Retorna uma tabela similar ao `/{{plataforma}}`, mas colapsando as linhas da mesma conta. As colunas numéricas são somadas, e as de texto ficam vazias (exceto o nome da conta).

**Exemplo de resposta:**
```csv
Platform,Ad Name,Clicks,Impressions,Cost
Facebook,,250,3000,120
YouTube,,150,2000,70
```

### 4. `/geral`
Retorna todos os anúncios de todas as plataformas, incluindo o nome da plataforma e da conta. As colunas são compostas por todos os campos de insights de todas as plataformas.

**Exemplo de resposta:**
```csv
Platform,Account,Ad Name,Clicks,Impressions,Cost,Cost per Click
Facebook,Account A,Ad 1,100,1000,50,0.5
YouTube,Account B,Ad 2,150,2000,70,0.47
```

### 5. `/geral/resumo`
Retorna uma tabela similar ao `/geral`, mas com as linhas agrupadas por plataforma. As colunas numéricas são somadas, e as de texto ficam vazias, exceto o nome da plataforma.

**Exemplo de resposta:**
```csv
Platform,Account,Clicks,Impressions,Cost
Facebook,,250,3000,120
YouTube,,150,2000,70
```

## Como Rodar o Projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/EudesLima224/teste-stract
cd seurepositorio
```

### 2. Criar um ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # No Linux/macOS
venv\Scripts\activate     # No Windows
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Rodar a API

```bash
python app.py
```

A API estará disponível em `http://localhost:5000`.

## Dependências

- Flask
- Requests

