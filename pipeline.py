from selenium import webdriver
import time
import pyautogui
import os
import shutil
import psycopg2
import pandas as pd
from pathlib import Path

root = Path(__file__).parent


# CAMINHO DAS PASTAS PARA OS ARQUIVOS
ROOT_ORIGIN = "C://Users//otavi//Downloads"
ROOT_DESTINY = Path(__file__).parent / 'CSV'
ROOT_COMPANY_NAMES = Path(__file__).parent / 'Company_names.csv'
list_name = []

# OBTENDO O NOME DOS TITULOS DAS EMPRESAS
with open(ROOT_COMPANY_NAMES, 'r', encoding='utf-8') as file:
    for i, name in enumerate(file):
        if i == 0:
            continue
        list_name.append(name)

# AUTOMATIZACAO PARA DOWLOAND DOS CSV DOS TITULOS DO MERCADO FINANCEIRO
def dowloand_titulos(name):
    drive = webdriver.Chrome()
    drive.get(f'https://br.financas.yahoo.com/quote/{name}/history')
    time.sleep(5)
    pyautogui.press('tab', 2)
    pyautogui.press('enter')
    drive.find_element('xpath','//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]').click()
    drive.find_element('xpath','//*[@id="dropdown-menu"]/div/ul[2]/li[4]/button').click()
    drive.find_element('xpath','//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/button').click()
    drive.find_element('xpath','//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[2]/span[2]/a').click()
    time.sleep(5)


# MOVENDO OS ARQUIVOS BAIXADO PARA PASTA CSV
def move_file(root_origin,root_destiny):
    arquivos = os.listdir(root_origin)
    for arquivo in arquivos:
        if arquivo.endswith('.csv'):
            caminho_original = os.path.join(root_origin, arquivo)
            caminho_destino = os.path.join(root_destiny, arquivo)
            shutil.move(caminho_original,caminho_destino)


# TRATAMENTO DOS DADOS
def data_processing(root_file):
    root_file_path = f'.//CSV//{root_file}.csv'
    bd = pd.read_csv(root_file_path)
    bd.dropna(inplace=True)
    bd.to_csv(root_file_path,index=False)

#CONECTANDO COM O BANCO DE DADOS
conn = psycopg2.connect(
    host="localhost",
    database="Acoes_b3",
    user="postgres",
    password="# INSIRA SUA SENHA DE ACESSO AO BANCO DE DADOS",
    port="5432"
)
    
#CRIANDO AS TABELAS DE ACORDO COM OS TITULOS
def create_table(name, name_file):
    table = f"""
        CREATE TABLE IF NOT EXISTS {name} (
            date DATE,
            open NUMERIC,
            high NUMERIC,
            low NUMERIC,
            close NUMERIC,
            adj_close NUMERIC,
            volume FLOAT
        )

    """
    cur = conn.cursor()
    cur.execute(table)
    conn.commit()

    # INSERINDO OS DADOS DENTRO DAS TABELAS
    def load_data(cur,file_path):
        with open (file_path,'r') as f:
            next(f)
            cur.copy_expert(sql=f"COPY {name} FROM STDIN CSV HEADER", file=f)
            conn.commit()
        print('Dados inseridos com suceso!')
    
    
    ROOT_FILE_PATH = f'.//CSV//{name_file}.csv'
    load_data(cur,ROOT_FILE_PATH)

# CHAMANDO A FUNCAO PARA FAZER DOWLOAND DOS TITULOS AUTOMATICAMENTE PASSANDO OS NOMES
for name in list_name:
    dowloand_titulos(name)

# CHAMANDO A FUNCAO MOVER TITULO PARA MOVER OS TITULOS PARA A PASTA DESTINO
move_file(ROOT_ORIGIN,ROOT_DESTINY)

# PROCESSANDO OS DADDOS PARA EXCLUIR OS NULL
for name in list_name:
    data_processing(name.split('\n')[0])

# CHAMANDO A FUNCAO PARA CRIAR AS TABELAS DE ACORDO COM OS TITULOS
for name in list_name:
    create_table(name.split('\n')[0].replace('.','_'), name.split('\n')[0])    