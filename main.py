import os
import time
import random
import sqlite3
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# --- CONFIGURAÇÕES ---
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(DIRETORIO_ATUAL, '.env'))
CAMINHO_BANCO = os.path.join(DIRETORIO_ATUAL, 'vagas.db')

# LÊ AS SENHAS APENAS 1 VEZ AO INICIAR
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID_GRUPO")

PALAVRAS_CHAVE = [
    "analista de dados", "business intelligence", "bi", "dados", "data", "pricing", 
    "comercial", "supervisão", "supervisor", "gerência", "gerente", "coordenação", 
    "coordenador", "economista", "inteligência de mercado", "inteligência de dados",
    "power bi", "python", "etl", "sql", "analista administrativo", "analista comercial",
    "vendedor", "vendedora", "vendas", "sdr", "bdr", "assistente comercial", 
    "comercial interno", "consultor comercial", "representante comercial",
    "executivo de vendas", "inside sales", "closer", "atendimento ao cliente", 
    "atendente", "balconista", "pós-venda", "assistente administrativa", 
    "assistente administrativo", "auxiliar administrativo", "administrativo", 
    "back office", "recepcionista", "recepção", "secretaria", "escola", "creche"
]

def vaga_nos_interessa(titulo):
    return any(palavra in titulo.lower() for palavra in PALAVRAS_CHAVE)

def iniciar_banco():
    conn = sqlite3.connect(CAMINHO_BANCO)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS vagas_enviadas (link TEXT, data_publicacao TEXT, titulo TEXT, PRIMARY KEY (link, data_publicacao))')
    conn.commit()
    return conn, cursor

def enviar_alerta_telegram(titulo, link, data, tags_texto):
    if not TOKEN or not CHAT_ID:
        print("ERRO: Credenciais ausentes no .env!")
        return False

    mensagem = f"🚨 *NOVA VAGA ENCONTRADA!*\n\n💼 *Vaga:* {titulo}\n🏷️ *Tags:* {tags_texto}\n📅 *Publicação:* {data}\n\n🔗 [Clique aqui para acessar]({link})"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown", "disable_web_page_preview": True}
    
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 429:
            pausa = r.json().get('parameters', {}).get('retry_after', 30)
            print(f"Pausa anti-spam de {pausa}s...")
            time.sleep(pausa)
            requests.post(url, json=payload)
            return True
        elif r.status_code == 200:
            print(f"✅ Alerta enviado: {titulo[:30]}...")
            return True
    except:
        print("❌ Falha na conexão com o Telegram.")
        return False

def buscar_vagas_refinadas():
    print("Iniciando varredura...")
    conn, cursor = iniciar_banco()
    
    opcoes = Options()
    opcoes.add_argument('--headless')
    opcoes.add_argument('--disable-gpu')
    opcoes.add_argument('--log-level=3')
    
    driver = webdriver.Chrome(options=opcoes)
    driver.set_page_load_timeout(30) # Reduzido para não agarrar o código por minutos
    
    pagina_atual = 1
    vagas_velhas = 0

    while vagas_velhas < 20 and pagina_atual <= 500:
        print(f"Página {pagina_atual}...")
        try:
            driver.get(f"https://riovagas.com.br/category/riovagas/page/{pagina_atual}/")
            time.sleep(random.uniform(3, 5))
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            artigos = soup.find_all('article')
            
            if not artigos: break

            for artigo in artigos:
                h2 = artigo.find('h2', class_='entry-title')
                if not h2 or not h2.find('a'): continue
                    
                titulo = h2.find('a').text.strip()
                link = h2.find('a').get('href')
                data = artigo.find('time').text.strip() if artigo.find('time') else "S/D"
                tags = ", ".join([t.text.strip() for t in artigo.find_all('a', rel='tag')])

                cursor.execute('SELECT 1 FROM vagas_enviadas WHERE link = ? AND data_publicacao = ?', (link, data))
                if cursor.fetchone():
                    vagas_velhas += 1
                    if vagas_velhas >= 20: break 
                else:
                    vagas_velhas = 0 
                    cursor.execute('INSERT INTO vagas_enviadas VALUES (?, ?, ?)', (link, data, titulo))
                    conn.commit()
                    
                    if vaga_nos_interessa(titulo):
                        enviar_alerta_telegram(titulo, link, data, tags)
                        time.sleep(3)
                        
        except Exception as e:
            print(f"⚠️ Erro ou Timeout na página {pagina_atual}. Pulando...")
            
        pagina_atual += 1

    driver.quit()
    conn.close()
    print("Varredura finalizada!")

if __name__ == '__main__':
    buscar_vagas_refinadas()
