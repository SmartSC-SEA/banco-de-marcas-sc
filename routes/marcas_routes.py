from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
from utils.db import connect_db
from utils.helpers import allowed_file, gerar_nome_unico, ALLOWED_EXTENSIONS, MAX_FILE_SIZE, admin_required
from werkzeug.utils import secure_filename
import os, MySQLdb, sys
from datetime import datetime, timedelta
from MySQLdb.cursors import DictCursor
from utils.db import connect_db


bp_marcas = Blueprint('marcas', __name__)


@bp_marcas.route('/cadastro_marca', methods=['GET', 'POST'])
def cadastro_marca():
    # proteção de sessão
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))

    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)

    if request.method == 'POST':
        # Campos simples
        codigo_item = request.form.get('codigo_item', '').strip().lower()
        descricao_produto = request.form.get('descricao_produto', '').strip()
        data_cadastro = request.form.get('data_cadastro', '').strip()
        data_validade = request.form.get('data_validade', '').strip()
        fornecedor_amostra = request.form.get('fornecedor_amostra', '').strip()
        processo_sgpe = request.form.get('processo_sgpe', '').strip()
        observacao = request.form.get('observacao', '').strip()
        fabricante = request.form.get('fabricante', '').strip()
        modelo = request.form.get('modelo', '').strip().lower()
        pais_origem = request.form.get('pais_origem', '').strip()
        id_orgao = request.form.get('id_orgao', '').strip()
        edital_pre_qualificacao = request.form.get('edital_pre_qualificacao', '').strip()
        marca = request.form.get('marca', '').strip().lower()

        # Tratamento de "outra" marca/modelo
        nova_marca = request.form.get('nova_marca', '').strip().lower()
        if marca == 'outra' and nova_marca:
            marca = nova_marca
        novo_modelo = request.form.get('modelo_novo', '').strip().lower()
        if modelo == 'outro' and novo_modelo:
            modelo = novo_modelo

        # Validações de arquivos está em dois grupos
        arquivos_unicos = {
            'arquivo_registro': request.files.get('arquivo_registro'),
            'arquivo_ficha_parecer': request.files.get('arquivo_ficha_parecer')
        }
        nomes_unicos = {}

        # Trata arquivos únicos
        for campo, arquivo in arquivos_unicos.items():
            if arquivo and arquivo.filename:
                filename = secure_filename(arquivo.filename)
                if not allowed_file(campo, filename):
                    permitidos = ', '.join(ALLOWED_EXTENSIONS[campo])
                    flash(f"Formato inválido em '{campo}': permitidos {permitidos}", 'warning')
                    return redirect(request.url)
                arquivo.seek(0, os.SEEK_END)
                if arquivo.tell() > MAX_FILE_SIZE:
                    flash(f"Arquivo em '{campo}' excede 10 MB.", 'warning')
                    return redirect(request.url)
                arquivo.seek(0)
                unique_name = gerar_nome_unico(filename)
                dest = os.path.join(upload_folder, unique_name)
                try:
                    arquivo.save(dest)
                except OSError as e:
                    current_app.logger.error(f"Erro salvando {campo}: {e}")
                    flash('Erro ao salvar arquivo, tente novamente mais tarde.', 'danger')
                    return redirect(request.url)
                nomes_unicos[campo] = unique_name

        # Trata múltiplas imagens
        imagens = request.files.getlist('imagens_produto')
        nomes_imagens = []
        for img in imagens:
            if img and img.filename:
                filename = secure_filename(img.filename)
                if not allowed_file('imagem_produto', filename):
                    flash('Formato inválido em imagem do produto.', 'warning')
                    return redirect(request.url)
                img.seek(0, os.SEEK_END)
                if img.tell() > MAX_FILE_SIZE:
                    flash('Uma das imagens excede 10 MB.', 'warning')
                    return redirect(request.url)
                img.seek(0)
                unique_img = gerar_nome_unico(filename)
                dest_img = os.path.join(upload_folder, unique_img)
                try:
                    img.save(dest_img)
                except OSError as e:
                    current_app.logger.error(f"Erro salvando imagem: {e}")
                    flash('Erro ao salvar imagem, tente novamente mais tarde.', 'danger')
                    return redirect(request.url)
                nomes_imagens.append(unique_img)

        # Conexão ao banco e inserção
        conn = connect_db()
        cursor = conn.cursor()
        # Verifica duplicidade
        cursor.execute(
            "SELECT COUNT(*) FROM marcas WHERE LOWER(codigo_item)=%s AND LOWER(marca)=%s AND LOWER(modelo)=%s",
            (codigo_item, marca, modelo)
        )
        if cursor.fetchone()[0] > 0:
            flash('Cadastro duplicado: código, marca e modelo já existem.', 'warning')
            cursor.close(); conn.close()
            return redirect(request.url)

        # Insere marca
        cursor.execute(
            '''INSERT INTO marcas (
                codigo_item, marca, descricao_produto, data_cadastro, data_validade,
                fornecedor_amostra, processo_sgpe, observacao,
                fabricante, modelo, pais_origem,
                arquivo_registro, arquivo_ficha_parecer, edital_pre_qualificacao,
                id_orgao, status_aprovacao
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
            (
                codigo_item, marca, descricao_produto, data_cadastro or None, data_validade or None,
                fornecedor_amostra, processo_sgpe, observacao,
                fabricante, modelo, pais_origem,
                nomes_unicos.get('arquivo_registro'), nomes_unicos.get('arquivo_ficha_parecer'), edital_pre_qualificacao,
                id_orgao or None, 'pendente'
            )
        )
        id_marca = cursor.lastrowid
        # Insere imagens
        for nome in nomes_imagens:
            cursor.execute(
                'INSERT INTO imagens_produto (id_marca, nome_arquivo) VALUES (%s, %s)',
                (id_marca, nome)
            )
        conn.commit()
        cursor.close()
        conn.close()

        flash('Marca cadastrada com sucesso!', 'success')
        return redirect(url_for('marcas.cadastro_marca'))

    # GET: prepara dados para o formulário
    conn = connect_db()
    cursor = conn.cursor(DictCursor)
    cursor.execute('SELECT * FROM orgaos ORDER BY nome_orgao')
    orgaos = cursor.fetchall()
    cursor.execute('SELECT DISTINCT marca FROM marcas ORDER BY marca')
    marcas_existentes = [row['marca'] for row in cursor.fetchall()]
    cursor.close(); conn.close()

    hoje = datetime.today().strftime('%Y-%m-%d')
    validade = (datetime.today() + timedelta(days=365)).strftime('%Y-%m-%d')

    return render_template(
        'cadastro_marca.html',
        hoje=hoje,
        validade=validade,
        orgaos=orgaos,
        marcas=marcas_existentes
    )

@bp_marcas.route('/consulta_marcas', methods=['GET', 'POST'])
def consulta_marcas():
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))

    marcas = []
    if request.method == 'POST':
        codigo_item = request.form.get('codigo_item','').strip()
        descricao = request.form.get('descricao','').strip()
        marca = request.form.get('marca','').strip()
        status_aprovacao = request.form.get('status_aprovacao','')




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
        marcas_raw = cursor.fetchall()

        # Verificar anexos para cada marca
        marcas = []
        for marca in marcas_raw:
            id_marca = marca['id']

            # Verifica se tem ao menos uma imagem ou documento
            cursor.execute('SELECT COUNT(*) as total FROM imagens_produto WHERE id_marca = %s', (id_marca,))
            tem_imagens = cursor.fetchone()['total'] > 0

            tem_documentos = False
            if marca['arquivo_registro'] or marca['arquivo_ficha_parecer']:
                tem_documentos = True

            marca['tem_anexos'] = tem_imagens or tem_documentos
            marcas.append(marca)


        cursor.close()
        conn.close()

    return render_template('consulta_marcas.html', marcas=marcas)

@bp_marcas.route('/editar_marca/<int:id>', methods=['GET', 'POST'])
def editar_marca(id):
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))

    conn = connect_db()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        marca = request.form.get('marca','').strip()
        nova_marca = request.form.get('nova_marca','').strip()
        modelo = request.form.get('modelo','').strip()
        modelo_novo = request.form.get('modelo_novo', '').strip()
        observacao = request.form.get('observacao','').strip()
        motivo = request.form.get('motivo','').strip()
        codigo_item = request.form.get('codigo_item','').strip()
        usuario = session.get('usuario')
        status_aprovacao = request.form.get('status_aprovacao','').strip()
        data_cadastro = request.form.get('data_cadastro','').strip()
        data_validade = request.form.get('data_validade','').strip()
        if session.get('perfil') != 'admin':
            status_aprovacao = 'pendente'

        marca = marca.strip().lower()
        modelo = modelo.strip().lower()

        if marca == 'outra' and nova_marca:
            marca = nova_marca
        if modelo == 'outro' and modelo_novo:
            modelo = modelo_novo

        # Verificar duplicidade da chave composta
        cursor.execute("""
            SELECT COUNT(*) AS total FROM marcas
            WHERE codigo_item = %s AND LOWER(marca) = %s AND LOWER(modelo) = %s AND id != %s
        """, (codigo_item, marca, modelo, id))
        resultado = cursor.fetchone()

        if resultado['total'] > 0:
            flash('Já existe outra marca cadastrada com este código de item, marca e modelo.', 'warning')
        else:
            # Atualiza e redireciona
            cursor.execute(
                'INSERT INTO log_alteracoes (id_marca, usuario, motivo) VALUES (%s, %s, %s)',
                (id, usuario, motivo)
            )
            cursor.execute(
                "UPDATE marcas SET marca = %s, modelo = %s, observacao = %s, status_aprovacao = %s, data_cadastro = %s, data_validade = %s WHERE id = %s",
                (marca, modelo, observacao, status_aprovacao, data_cadastro, data_validade, id)
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash('Marca atualizada com sucesso!', 'success')
            return redirect(url_for('marcas.consulta_marcas'))

        # Se houver duplicidade, reexibir a tela com os dados preenchidos
        cursor.execute('SELECT * FROM marcas WHERE id = %s', (id,))
        marca_atual = cursor.fetchone()

        cursor.execute('SELECT nome_arquivo FROM imagens_produto WHERE id_marca = %s', (id,))
        imagens = [row['nome_arquivo'] for row in cursor.fetchall()]

        cursor.execute('SELECT DISTINCT marca FROM marcas ORDER BY marca')
        marcas = [row['marca'] for row in cursor.fetchall()]

        cursor.execute('SELECT * FROM orgaos ORDER BY nome_orgao')
        orgaos = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('editar_marca.html', marca=marca_atual, imagens=imagens, marcas=marcas, orgaos=orgaos)

    # GET
    cursor.execute('SELECT * FROM marcas WHERE id = %s', (id,))
    marca = cursor.fetchone()

    if not marca:
        flash('Marca não encontrada.')
        return redirect(url_for('marcas.consulta_marcas'))

    cursor.execute('SELECT nome_arquivo FROM imagens_produto WHERE id_marca = %s', (id,))
    imagens = [row['nome_arquivo'] for row in cursor.fetchall()]

    cursor.execute('SELECT DISTINCT marca FROM marcas ORDER BY marca')
    marcas = [row['marca'] for row in cursor.fetchall()]

    cursor.execute('SELECT * FROM orgaos ORDER BY nome_orgao')
    orgaos = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('editar_marca.html', marca=marca, imagens=imagens, marcas=marcas, orgaos=orgaos)


@bp_marcas.route('/marcas_existentes', methods=['POST'])
def marcas_existentes():
    codigo_item = request.form.get('codigo_item','').strip()
    conn = connect_db()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("SELECT codigo_item, processo_sgpe, marca, fornecedor_amostra, observacao FROM marcas WHERE codigo_item = %s", (codigo_item,))
    registros = cursor.fetchall()

    cursor.close()
    conn.close()

    return {'marcas': registros}

@bp_marcas.route('/modelos_por_marca', methods=['POST'])
def modelos_por_marca():
    marca = request.form.get('marca','').strip()
    conn = connect_db()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT DISTINCT modelo FROM marcas WHERE marca = %s ORDER BY modelo", (marca,))
    modelos = [row['modelo'] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify({'modelos': modelos})



