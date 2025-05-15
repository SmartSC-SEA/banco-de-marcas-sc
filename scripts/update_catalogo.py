#!/usr/bin/env python3
"""
Script para carregamento completo ou incremental dos itens do SIPAC
para a tabela local `catalogo_itens` no banco de cadastro_marcas.
"""
import os
import sys
import time
import logging
import argparse
import requests
import urllib
from datetime import datetime
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import pooling, Error

# Carrega variáveis de ambiente de /etc/banco-de-marcas/.env
load_dotenv('/etc/banco-de-marcas/.env')


# Configuração de logging
LOG_FILE = '/var/log/banco-marcas/catalogo.log'
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)


# DB pool
DB_CONFIG = {
    'host':     os.getenv('DB_HOST'),
    'user':     os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'pool_name': 'catalogo_pool',
    'pool_size': 3
}
try:
    db_pool = mysql.connector.pooling.MySQLConnectionPool(**DB_CONFIG)
except Error as e:
    logging.critical(f'Erro criando pool MySQL: {e}')
    sys.exit(1)

def conectar_banco():
    return db_pool.get_connection()

# API config
LOGIN_URL    = os.getenv('CATALOG_LOGIN_URL')
BASE_URL     = os.getenv('CATALOG_BASE_URL')
ENDPOINT     = os.getenv('CATALOG_ENDPOINT')  
CLIENT_TOKEN = os.getenv('CATALOG_CLIENT_TOKEN')
USERNAME     = os.getenv('CATALOG_USER')
PASSWORD     = os.getenv('CATALOG_PASS')

# Token globals
access_token = None
refresh_token = None
token_expiry  = 0

# Authentication functions

def obter_token(refresh=False):
    global access_token, refresh_token, token_expiry
    payload = {'grant_type': 'refresh_token' if refresh else 'password'}
    if refresh and refresh_token:
        payload['refresh_token'] = refresh_token
    else:
        payload.update({'username': USERNAME, 'password': PASSWORD})
    headers = {'Authorization': CLIENT_TOKEN,
               'Content-Type': 'application/x-www-form-urlencoded'}
    resp = requests.post(LOGIN_URL, data=payload, headers=headers, timeout=10)
    if not resp.ok:
        logging.error(f'Falha ao obter token: {resp.status_code} {resp.text}')
        return None
    data = resp.json()
    access_token  = data['access_token']
    refresh_token = data.get('refresh_token', refresh_token)
    token_expiry  = time.time() + data['expires_in'] - 20
    logging.info('Access_token obtido')
    return access_token

# Decorator to ensure valid token

def token_required(func):
    def wrapper(*args, **kwargs):
        global access_token, token_expiry
        if not access_token or time.time() > token_expiry:
            success = obter_token(refresh=bool(access_token))
            if not success:
                sys.exit('Não foi possível autenticar')
        return func(*args, **kwargs)
    return wrapper

# Common fetch loop
def fetch_and_upsert(endpoint_url, params=None):
    conn   = conectar_banco()
    cursor = conn.cursor()
    page   = 1
    total  = 0
    while True:
        url = f"{BASE_URL}{endpoint_url.format(page)}"
        headers = {'Authorization': f'Bearer {access_token}'}
        logging.info(f'Buscando página {page}: {url}')
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            logging.warning(f'Erro status {resp.status_code} na página {page}'); time.sleep(5); continue
        try:
            dados = resp.json().get('content', [])
        except Exception as e:
            logging.warning(f'JSON inválido na página {page}: {e}'); time.sleep(5); continue
        if not dados:
            break
        for item in dados:
            codigo = (item.get('itemCodigo') or '').strip()
            desc   = (item.get('itemDescricao') or '').strip()
            if not codigo:
                continue
            cursor.execute(
                'INSERT INTO catalogo_itens (item_codigo, item_descricao) VALUES (%s,%s) '
                'ON DUPLICATE KEY UPDATE item_descricao=VALUES(item_descricao)',
                (codigo, desc)
            )
            total += 1
        conn.commit()
        page += 1
        time.sleep(1)
    cursor.close(); conn.close()
    logging.info(f'Upsert finalizado: {total} registros')
    return total

@token_required
def full_load():
    """Carrega todo o catálogo de uma só vez."""
    logging.info('Iniciando full load do catálogo')
    count = fetch_and_upsert(ENDPOINT)
    logging.info(f'Full load completo: {count} registros processados')

@token_required
def incremental_load():
    """Carrega apenas itens aprovados após a última atualização."""
    # lê última data
    q = "SELECT data_ultima FROM catalogo_controle ORDER BY id DESC LIMIT 1"
    conn = conectar_banco(); cur = conn.cursor()
    cur.execute(q)
    last = cur.fetchone()[0] if cur.fetchone() else '2000-01-01T00:00:00'
    conn.close()
    # format date for URL
    dt = urllib.parse.quote_plus(last)
    endpoint = f"/integracao/itens/atualizados/porPeriodo?situacaoDoItem=ATIVO&dataDeCorte={dt}&page={{}}&size=100"
    logging.info(f'Iniciando incremental a partir de {last}')
    count = fetch_and_upsert(endpoint)
    # atualiza controle
    now = datetime.utcnow().isoformat()
    conn = conectar_banco(); cur = conn.cursor()
    cur.execute('UPDATE catalogo_controle SET data_ultima=%s', (now,))
    conn.commit(); conn.close()
    logging.info(f'Incremental completo: {count} registros processados')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Atualização do catálogo')
    parser.add_argument('mode', choices=['full','inc'], help='Modo: full load ou incremental')
    args = parser.parse_args()
    if args.mode == 'full':
        full_load()
    else:
        incremental_load()
