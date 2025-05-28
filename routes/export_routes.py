from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, make_response, current_app
from utils.db import connect_db
import os, MySQLdb
from xhtml2pdf import pisa
from io import BytesIO
from datetime import datetime


bp_export = Blueprint('export', __name__)

@bp_export.route('/exportar_pdf', methods=['POST'])
def exportar_pdf():
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))

    codigo_item = request.form.get('codigo_item','').strip()
    descricao = request.form.get('descricao','').strip()
    marca = request.form.get('marca','').strip()
    status_aprovacao = request.form.get('status_aprovacao','').strip()

    conn = connect_db()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    query = "SELECT * FROM marcas WHERE 1=1"
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
    if status_aprovacao:
        query += " AND status_aprovacao = %s"
        params.append(status_aprovacao)

    cursor.execute(query, params)
    marcas = cursor.fetchall()
    cursor.close()
    conn.close()

    logo_path = os.path.join(current_app.root_path, 'static', 'img', 'logo_pdf.png')

    html = render_template('pdf_template.html', marcas=marcas, now=datetime.now(), usuario=session.get('usuario'),logo_path=logo_path)

    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)

    if pisa_status.err:
        return "Erro ao gerar PDF", 500

    response = make_response(result.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=marcas_consulta.pdf'
    return response

@bp_export.route('/anexos_marca/<int:id>')
def anexos_marca(id):
    conn = connect_db()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("SELECT nome_arquivo FROM imagens_produto WHERE id_marca = %s", (id,))
    imagens = [row['nome_arquivo'] for row in cursor.fetchall()]

    cursor.execute("SELECT arquivo_registro, arquivo_ficha_parecer FROM marcas WHERE id = %s", (id,))
    doc = cursor.fetchone()
    documentos = []
    if doc:
        if doc['arquivo_registro']:
            documentos.append(doc['arquivo_registro'])
        if doc['arquivo_ficha_parecer']:
            documentos.append(doc['arquivo_ficha_parecer'])

    cursor.close()
    conn.close()

    return jsonify({'imagens': imagens, 'documentos': documentos})
