from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.db import connect_db
import os, MySQLdb
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash

bp_auth = Blueprint('auth', __name__)

@bp_auth.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cpf = request.form.get('cpf','').strip()
        senha = request.form.get('senha')



        conn = connect_db()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('SELECT * FROM usuarios WHERE cpf = %s', (cpf,))
        user = cursor.fetchone()
        print('DEBUG: user retornado =', user)  # <-- adicione isso

        cursor.close()
        conn.close()
        session.permanent = True
        if user and check_password_hash(user['senha'], senha):
            session['cpf'] = cpf
            session['perfil'] = user['perfil']
            session['usuario'] = user['usuario']
            return redirect(url_for('auth.home'))
        else:
            flash('Usuário ou senha inválidos.')
            return redirect(url_for('auth.login'))

    return render_template('login.html')


@bp_auth.route('/home')
def home():
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))

    conn = connect_db()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    # Calcular a data limite (hoje + 60 dias)
    hoje = datetime.today()
    limite = hoje + timedelta(days=60)

    # Buscar marcas com validade até a data limite
    query = """
        SELECT * FROM marcas
        WHERE data_validade BETWEEN %s AND %s
        ORDER BY data_validade ASC
    """
    cursor.execute(query, (hoje.strftime('%Y-%m-%d'), limite.strftime('%Y-%m-%d')))
    vencimentos = cursor.fetchall()

    if session.get('perfil') == 'admin':
        cursor.execute("""
            SELECT id, codigo_item, marca, modelo
            FROM marcas
            WHERE status_aprovacao = 'pendente'
            ORDER BY codigo_item
            LIMIT 20
        """)
        marcas_pendentes = cursor.fetchall()
    else:
        marcas_pendentes = []


    cursor.close()
    conn.close()


    return render_template('home.html', vencimentos=vencimentos,marcas_pendentes=marcas_pendentes)


@bp_auth.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('auth.login'))
