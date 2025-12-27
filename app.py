
import requests
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from flask import Flask, render_template

app = Flask(__name__)

# Função para limpar e converter valores numéricos
def limpar_valor(valor):
    try:
        return float(valor.replace(".", "").replace(",", "."))
    except ValueError:
        return valor

# Função para realizar o Web Scraping
def coletar_cotacoes():
    url = "https://br.investing.com/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)

    # Valida a resposta
    if response.status_code != 200:
        raise Exception("Erro ao acessar a página.")

    # Parse do conteúdo HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Localiza a tabela de cotações
    tabela = soup.find("tbody", {"class": "datatable-v2_body__8TXQk"})

    # Coleta os dados das linhas
    linhas = tabela.find_all("tr")

    # Identifica os nomes das colunas (cabeçalhos)
    cabecalhos = [th.text.strip() for th in tabela.find_previous("thead").find_all("th")]

    # Coleta os dados das colunas
    dados = []
    for linha in linhas:
        colunas = [col.text.strip() for col in linha.find_all("td")]
        if colunas:
            dados.append(colunas)

    # Cria um DataFrame com os dados
    df = pd.DataFrame(dados, columns=cabecalhos)

    # Salva os dados em CSV
    df.to_csv("cotacoes.csv", index=False, encoding='utf-8-sig')
    print("Arquivo CSV gerado com sucesso!")

    return df

# Função para gerar um gráfico personalizado
def gerar_grafico(df):
    # Ajustando nomes das colunas conforme a imagem
    # Supondo que df.columns[0] é 'Nome' e df.columns[5] é 'Var. %'
    nomes = df.iloc[:, 0]
    
    # Limpa a variação percentual (remove o símbolo '%' e converte)
    variacoes = df.iloc[:, 5].str.replace('%', '').apply(limpar_valor)

    plt.figure(figsize=(12, 6))
    
    # Cores condicionais: Verde para alta, Vermelho para baixa
    cores = ['#4CAF50' if x > 0 else '#F44336' for x in variacoes]
    
    plt.bar(nomes, variacoes, color=cores)

    plt.title('Variação Percentual dos Índices Globais', fontsize=16, fontweight='bold')
    plt.xlabel('Índice', fontsize=12)
    plt.ylabel('Variação (%)', fontsize=12)
    plt.axhline(0, color='black', linewidth=0.8, linestyle='--') # Linha no zero
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/grafico_variacao.png')
    print("Gráfico gerado com sucesso!")

@app.route('/')
def index():
    # Coletar cotações e gerar gráfico
    df = coletar_cotacoes()
    gerar_grafico(df)

    # Converter DataFrame para HTML
    tabela_html = df.to_html(index=False, classes="table table-striped")

    return render_template('index.html', tabela_html=tabela_html)

if __name__ == '__main__':
    app.run(debug=True)
