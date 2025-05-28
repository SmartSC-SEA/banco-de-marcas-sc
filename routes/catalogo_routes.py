from flask import Blueprint, request, session, redirect, url_for
from utils.db import connect_db
import  MySQLdb

bp_catalogo = Blueprint('catalogo', __name__)

@bp_catalogo.route('/buscar_catalogo', methods=['POST'])
def buscar_catalogo():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    termo = request.form.get('termo','').strip()  # pode ser código ou descrição
    tipo_busca = request.form.get('tipo_busca')  # 'codigo' ou 'descricao'

    conn = connect_db()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    if tipo_busca == 'codigo':
        query = "SELECT item_codigo, item_descricao FROM catalogo_itens WHERE item_codigo LIKE %s order by item_descricao ASC"
        cursor.execute(query, (f"%{termo}%",))
    else:
        query = "SELECT item_codigo, item_descricao FROM catalogo_itens WHERE item_descricao LIKE %s order by item_descricao ASC"
        cursor.execute(query, (f"%{termo}%",))

    resultados = [
        {
            'itemCodigo': row['item_codigo'],
            'itemDescricao': row['item_descricao'] or ''
        }
        for row in cursor.fetchall()
    ]

    cursor.close()
    conn.close()

    return {'resultados': resultados}
