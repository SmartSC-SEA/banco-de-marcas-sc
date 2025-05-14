from flask import Blueprint, request, session, redirect, url_for
from utils.db import connect_catalogo
import  MySQLdb

bp_catalogo = Blueprint('catalogo', __name__)

@bp_catalogo.route('/buscar_catalogo', methods=['POST'])
def buscar_catalogo():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    termo = request.form.get('termo','').strip()  # pode ser código ou descrição
    tipo_busca = request.form.get('tipo_busca')  # 'codigo' ou 'descricao'

    conn = connect_catalogo()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    if tipo_busca == 'codigo':
        query = "SELECT itemCodigo, itemDescricao FROM materiais WHERE itemCodigo LIKE %s AND itemSituacao = 'ativo' order by itemSituacao, itemDescricao ASC"
        cursor.execute(query, (f"%{termo}%",))
    else:
        query = "SELECT itemCodigo, itemDescricao FROM materiais WHERE itemDescricao LIKE %s AND itemSituacao = 'ativo' order by itemSituacao, itemDescricao ASC"
        cursor.execute(query, (f"%{termo}%",))

    resultados = cursor.fetchall()
    cursor.close()
    conn.close()

    return {'resultados': resultados}
