import os
import time
import random
import sqlite3
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

load_dotenv()

# --- 1. A SUPER LISTA UNIFICADA DE PALAVRAS-CHAVE ---
PALAVRAS_CHAVE = [
    # Lucas (Dados/Gestão)
    "analista de dados", "business intelligence", "bi", "dados", "data", "pricing", 
    "comercial", "supervisão", "supervisor", "gerência", "gerente", "coordenação", 
    "coordenador", "economista", "inteligência de mercado", "inteligência de dados",
    "power bi", "python", "etl", "sql", "analista administrativo", "analista comercial",
    
    # Chico & Mariane (Vendas/Atendimento/Administrativo)
    "vendedor", "vendedora", "vendas", "sdr", "bdr", "assistente comercial", 
    "comercial interno", "consultor comercial", "representante comercial",
    "executivo de vendas", "inside sales", "closer", "atendimento ao cliente", 
    "atendente", "balconista", "pós-venda", "assistente administrativa", 
    "assistente administrativo", "auxiliar administrativo", "administrativo", 
    "back office", "recepcionista", "recepção", "secretaria", "escola", "creche"
]

def vaga_nos_interessa(titulo):
    titulo_lower = titulo.lower()
    # Verifica se alguma palavra da nossa lista está no título da vaga
    return any(palavra in titulo_lower for palavra in PALAVRAS_CHAVE)

# --- 2. BANCO DE DADOS ---
def iniciar_banco():
    conn = sqlite3.connect('vagas.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vagas_enviadas (
            link TEXT,
            data_publicacao TEXT,
            titulo TEXT,
            data_descoberta DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (link, data_publicacao)
        )
    ''')
    conn.commit()
    return conn, cursor

def ja_existe_no_banco(cursor, link, data_publicacao):
    cursor.execute('SELECT 1 FROM vagas_enviadas WHERE link = ? AND data_publicacao = ?', (link, data_publicacao))
    return cursor.fetchone() is not None

def salvar_no_banco(conn, cursor, link, data_publicacao, titulo):
    cursor.execute('INSERT INTO vagas_enviadas (link, data_publicacao, titulo) VALUES (?, ?, ?)', (link, data_publicacao, titulo))
    conn.commit()

# --- 3. DISPARO PARA O TELEGRAM ---
def enviar_alerta_telegram(titulo, link, data, tags_texto):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("CHAT_ID_GRUPO") 

    mensagem = f"🚨 *NOVA VAGA ENCONTRADA!*\n\n" \
               f"💼 *Vaga:* {titulo}\n" \
               f"🏷️ *Tags:* {tags_texto}\n" \
               f"📅 *Publicação:* {data}\n\n" \
               f"🔗 [Clique aqui para acessar]({link})"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": mensagem,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Erro no envio do Telegram: {e}")

# --- 4. MOTOR DE BUSCA ---
def buscar_vagas_refinadas():
    conn, cursor = iniciar_banco()
    
    opcoes = Options()
    opcoes.add_argument('--headless')
    opcoes.add_argument('--disable-gpu')
    opcoes.add_argument('--log-level=3')
    opcoes.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=opcoes)
    
    pagina_atual = 1
    vagas_velhas_seguidas = 0
    LIMITE_VELHAS = 10

    while vagas_velhas_seguidas < LIMITE_VELHAS:
        url = f"https://riovagas.com.br/category/riovagas/page/{pagina_atual}/"
        
        try:
            driver.get(url)
            time.sleep(random.uniform(4.5, 7.5))
        except:
            time.sleep(10)
            continue
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        artigos = soup.find_all('article')
        
        if not artigos:
            break

        for artigo in artigos:
            h2 = artigo.find('h2', class_='entry-title')
            if not h2: continue
            
            tag_a = h2.find('a')
            if not tag_a: continue
                
            titulo = tag_a.text.strip()
            link = tag_a.get('href')

            # Extraindo a Data
            tag_time = artigo.find('time')
            data_publicacao = tag_time.text.strip() if tag_time else "Data Desconhecida"

            elementos_tags = artigo.find_all('a', rel='tag')
            if elementos_tags:
                tags_texto = ", ".join([t.text.strip() for t in elementos_tags])
            else:
                tags_texto = "Não informadas"

            if ja_existe_no_banco(cursor, link, data_publicacao):
                vagas_velhas_seguidas += 1
                if vagas_velhas_seguidas >= LIMITE_VELHAS:
                    break 
            else:
                vagas_velhas_seguidas = 0 
                salvar_no_banco(conn, cursor, link, data_publicacao, titulo)
                
                # Se a vaga tem uma de nossas palavras-chave, enviamos o alerta
                if vaga_nos_interessa(titulo):
                    enviar_alerta_telegram(titulo, link, data_publicacao, tags_texto)
        
        if vagas_velhas_seguidas >= LIMITE_VELHAS:
            break
            
        pagina_atual += 1
        if pagina_atual >500: 
            break

    driver.quit()
    conn.close()

if __name__ == '__main__':
    buscar_vagas_refinadas()