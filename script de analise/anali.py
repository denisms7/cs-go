import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.offline as pyo
import locale


# Defina o idioma desejado
idioma = 'pt_BR.UTF-8'

# Altere a configuração regional
locale.setlocale(locale.LC_ALL, idioma)


url2015 = "https://beitacao-csgo.vercel.app/2015.html"
url2016 = "https://beitacao-csgo.vercel.app/2016.html"
url2017 = "https://beitacao-csgo.vercel.app/2017.html"
url2018 = "https://beitacao-csgo.vercel.app/2018.html"
url2019 = "https://beitacao-csgo.vercel.app/2019.html"
url2020 = "https://beitacao-csgo.vercel.app/2020.html"
url2021 = "https://beitacao-csgo.vercel.app/2021.html"
url2022 = "https://beitacao-csgo.vercel.app/2022.html"


urls = [url2015, url2016, url2017, url2018, url2019, url2020, url2021, url2022]
anos = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]


def Scrap(url, ano):
    url = url
    ano = ano

    # Fazer uma requisição HTTP GET
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')

    # Criar listas para armazenar os cabeçalhos e os dados
    headers = []
    data = []

    # Extrair os cabeçalhos da tabela
    for th in table.find_all('th'):
        headers.append(th.text.strip())

    # Extrair os dados da tabela
    for row in table.find_all('tr'):
        row_data = []
        for td in row.find_all('td'):
            row_data.append(td.text.strip())
        if row_data:
            data.append(row_data)

    base = pd.DataFrame(data, columns=headers)
    base['Ano'] = ano

    return base


dfs = []

# Loop for para percorrer as variáveis url e ano
for url, ano in zip(urls, anos):
    df = Scrap(url, ano)
    dfs.append(df)

df_final = pd.concat(dfs, ignore_index=True)


# Deleta coluna Teams
df_final = df_final.drop(columns=['Teams'])

# Converter colunas
df_final['Ano'] = df_final['Ano'].astype(int)
df_final['Maps'] = df_final['Maps'].astype(int)
df_final['Rounds'] = df_final['Rounds'].astype(int)
df_final['K/D'] = pd.to_numeric(df_final['K/D'])
df_final['Rating1.0'] = pd.to_numeric(df_final['Rating1.0'])
df_final['Rating2.0'] = pd.to_numeric(df_final['Rating2.0'])


# Proporcao K/D por Rounds
df_final['Rounds/KD'] = df_final['K/D'] / df_final['Rounds']


# Primeiro, dividimos a coluna 'K/D' pela coluna 'Rounds' para obter a relação Rounds/KD e armazenamos o resultado na nova coluna 'Rounds/KD' do DataFrame df_final.


df_kd_rounds = df_final.groupby('Ano')['Rounds/KD'].sum().reset_index()
df_kd_total = df_final.groupby('Ano')['K/D'].sum().reset_index()
df_mapas_total = df_final.groupby('Ano')['Maps'].sum().reset_index()


fig1 = px.line(title='Relação K/D e Rounds por ano TOP 30 HLTV')

# Adiciona linha Rounds/KD
fig1.add_scatter(
    x=df_kd_rounds['Ano'], y=df_kd_rounds['Rounds/KD'], name='Relação K/D e Rounds')

fig1.update_layout(xaxis_title='Ano', yaxis_title='Rounds/KD')

fig2 = px.line(title='Soma de K/D por ano TOP 30 HLTV')

# Adiciona linha KD
fig2.add_scatter(x=df_kd_total['Ano'], y=df_kd_total['K/D'], name='KD')

fig2.update_layout(xaxis_title='Ano', yaxis_title='Valor')


fig3 = px.line(title='Soma de Mapas por ano TOP 30 HLTV')

# Adiciona linha Rounds
fig3.add_scatter(x=df_mapas_total['Ano'],
                 y=df_mapas_total['Maps'], name='Maps')

fig3.update_layout(xaxis_title='Ano', yaxis_title='Quantidade')


# Box Plot KD
fig11 = px.box(df_final, x='Ano', y=['K/D'])
fig11.update_layout(
    title="Top 30 HLTV K/D",
    yaxis_title='Rating',
)


# Box Plot Rating
fig12 = px.box(df_final, x='Ano', y=['Rating1.0', 'Rating2.0'])
fig12.update_layout(
    title="Top 30 HLTV Rating",
    yaxis_title='Rating',
    annotations=[
        dict(
                x=1,
                y=1.05,
                text="2015 e 2016 = Rating1.0 | 2017 a 2022 = Rating2.0",
                showarrow=False,
                xref="paper",
                yref="paper",
                font=dict(size=10)
        )
    ]
)


caminho = r'C:\PROJETOS\cs-go\graficos'


fig1.write_html(caminho + '\grafico1.html')
fig2.write_html(caminho + '\grafico2.html')
fig3.write_html(caminho + '\grafico3.html')
fig11.write_html(caminho + '\grafico4.html')
fig12.write_html(caminho + '\grafico5.html')
