from flask import Blueprint, render_template, request, current_app, send_from_directory
from utils.db import connect_db
from utils.helpers import limiter
import  MySQLdb

bp_public = Blueprint('public', __name__)

@bp_public.route('/consulta_publica', methods=['GET', 'POST'])
@limiter.limit("10 per minute") 
def consulta_publica():
    marcas = []
    if request.method == 'POST':
        codigo_item = request.form.get('codigo_item','').strip()
        descricao = request.form.get('descricao','').strip()
        marca = request.form.get('marca','').strip()

        conn = connect_db()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        query = "SELECT * FROM marcas WHERE status_aprovacao = 'aprovado'"
        params = []

        if codigo_item:
            query += " AND codigo_item LIKE %s"
            params.append(f"%{codigo_item}%")
        if descricao:
            query += " AND descricao_produto LIKE %s"
            params.append(f"%{descricao}%")
        if marca:
            query += " AND marca LIKE %s"
            params.append(f"%{marca}%")

        cursor.execute(query, params)
        marcas = cursor.fetchall()
    
        cursor.close()
        conn.close()

    return render_template('consulta_publica.html', marcas=marcas)

@bp_public.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """
    Serve um arquivo que está no diretório UPLOAD_FOLDER.
    """
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=False
    )
