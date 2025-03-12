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
    # Seleciona as colunas desejadas (Compra e Venda)
    moedas = df.iloc[:, 0]               # Primeira coluna (Moeda ou Ativo)
    valores_compra = df.iloc[:, 2].apply(limpar_valor)  # Terceira coluna (Compra)
    valores_venda = df.iloc[:, 3].apply(limpar_valor)   # Quarta coluna (Venda)

    # Personalização do gráfico
    plt.figure(figsize=(14, 8))  # Tamanho do gráfico (largura, altura)

    # Cria um gráfico de barras para Compra e Venda
    plt.bar(moedas, valores_compra, color='#4CAF50', label='Compra', alpha=0.8)
    plt.bar(moedas, valores_venda, color='#F44336', label='Venda', alpha=0.7)

    # Personaliza Título e Eixos
    plt.title('Comparação de Cotações - Compra vs Venda', fontsize=18, fontweight='bold')
    plt.xlabel('Moedas ou Ativos', fontsize=14)
    plt.ylabel('Valor (R$)', fontsize=14)

    # Rotaciona os rótulos no eixo X
    plt.xticks(rotation=45, fontsize=12)

    # Adiciona a legenda no canto superior direito
    plt.legend(loc='upper right', fontsize=12)

    # Destaca a moeda com o maior valor de compra
    maximo = valores_compra.idxmax()
    plt.annotate(f'Máx: {moedas[maximo]} - R${valores_compra[maximo]:,.2f}',
                 xy=(maximo, valores_compra[maximo]),
                 xytext=(maximo, valores_compra[maximo] + 1),
                 arrowprops=dict(facecolor='blue', shrink=0.05),
                 fontsize=12, color='blue')

    # Ajusta o layout para evitar cortes
    plt.tight_layout()

    # Salva o gráfico em static/
    plt.savefig('static/grafico.png')
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
