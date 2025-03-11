import requests
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from flask import Flask, render_template

app = Flask(__name__)

# Função para limpar e converter valores numéricos
def limpar_valor(valor):
    # Remove os pontos e troca a vírgula por ponto
    return float(valor.replace(".", "").replace(",", "."))

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

    # Prepara a lista de cotações
    dados = []

    for linha in linhas[1:]:
        colunas = linha.find_all("td")
        if len(colunas) >= 5:
            moeda = colunas[0].text.strip()
            try:
                compra = limpar_valor(colunas[2].text.strip())
                venda = limpar_valor(colunas[3].text.strip())
            except ValueError:
                print(f"Erro ao converter valores: {colunas[2].text}, {colunas[3].text}")
                continue
            variacao = colunas[4].text.strip()
            dados.append([moeda, compra, venda, variacao])

    # Cria um DataFrame com os dados
    df = pd.DataFrame(dados, columns=["Moeda", "Compra", "Venda", "Variação"])
    
    # Salva em CSV
    df.to_csv("cotacoes.csv", index=False, encoding='utf-8-sig')
    print("Arquivo CSV gerado com sucesso!")

    return df

# Função para gerar gráfico e salvar em static/
def gerar_grafico(df):
    plt.figure(figsize=(10, 6))
    plt.bar(df["Moeda"], df["Compra"], color='green', label='Compra')
    plt.bar(df["Moeda"], df["Venda"], color='red', label='Venda', alpha=0.7)

    plt.title('Comparação de Cotações (Compra vs. Venda)')
    plt.xlabel('Moeda')
    plt.ylabel('Valor (R$)')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Salva o gráfico como imagem
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
