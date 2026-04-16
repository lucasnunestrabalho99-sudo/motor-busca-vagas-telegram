# 🚀 Motor de Busca e Alertas de Vagas (Telegram Bot)

Uma ferramenta automatizada de Web Scraping e inteligência de dados desenvolvida em Python. Este projeto extrai, filtra e notifica oportunidades de emprego em tempo real, substituindo a busca manual diária por um fluxo contínuo de dados. Os alertas são enviados diretamente para um grupo no Telegram com base em palavras-chave pré-configuradas.

## 📸 Demonstração
<img width="913" height="273" alt="image (10)" src="https://github.com/user-attachments/assets/1fd32d21-53b9-4760-bddd-f42b32d2ecb4" />

## ⚙️ Arquitetura e Funcionalidades

* **Bypass de Segurança:** Utiliza `Selenium` (modo headless) e `BeautifulSoup` para contornar bloqueios de segurança e extrair dados dinâmicos da web.
* **Filtro Inteligente:** Processa os títulos e metadados das vagas, cruzando as informações com uma lista customizável de palavras-chave para diferentes perfis profissionais.
* **Memória de Estado (SQLite):** Implementa um banco de dados relacional leve para registrar o histórico de oportunidades. O algoritmo possui uma lógica de parada (*Stop Condition*) que interrompe a varredura ao encontrar vagas repetidas, otimizando o tempo de execução e o consumo de recursos.
* **Notificação em Tempo Real:** Integração com a API REST do Telegram para disparar as vagas aprovadas diretamente para o usuário.
* **Execução em Background:** Scripts `.bat` e `.vbs` configurados para rodar a automação de forma 100% invisível via Agendador de Tarefas do Windows.

---

## 🛠️ Como Clonar e Utilizar

Se você deseja rodar este projeto localmente, siga as instruções abaixo:

### 1. Pré-requisitos
* [Python 3](https://www.python.org/downloads/) instalado.
* Google Chrome instalado.
* Um Bot criado no Telegram (via `@BotFather`) e seu respectivo `Token`.

### 2. Instalação e Ambiente
Clone este repositório e acesse a pasta do projeto:
```bash
git clone https://github.com/lucasnunestrabalho99-sudo/motor-busca-vagas-telegram.git
cd motor-busca-vagas-telegram
```
Crie e ative um ambiente virtual padrão do Python, e instale as dependências:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
### 3. Configuração de Credenciais (.env)
Por diretrizes de segurança, o arquivo `.env` foi ignorado no repositório. Crie um arquivo chamado `.env` na raiz do projeto e adicione as suas credenciais:
```bash
TELEGRAM_TOKEN=seu_token_gerado_no_botfather
CHAT_ID_GRUPO=-id_do_seu_grupo_aqui
```
*(Dica: Para descobrir o ID do seu grupo, adicione temporariamente o bot `@RawDataBot` a ele).*

### 4. Execução
Para testar a extração manualmente no terminal:
```bash
python main.py
```
Para rodar de forma automatizada e contínua no Windows:
1. Abra o **Agendador de Tarefas**.
2. Crie uma nova tarefa e defina a execução para a cada 30 minutos.
3. Na aba "Ações", aponte para o arquivo `invisivel.vbs`.
4. No campo "Iniciar em", cole o caminho absoluto da pasta raiz do seu projeto.

---

## 💻 Stack Tecnológica

* **Linguagem:** Python 3
* **Extração e Parsing:** Selenium WebDriver, BeautifulSoup4
* **Banco de Dados:** SQLite
* **Integração:** Requests (Telegram Bot API)
* **Gerenciamento de Variáveis:** Python-dotenv
* **Sistema:** VBScript e Batch (Automatização no Windows)
