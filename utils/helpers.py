import uuid
from functools import wraps
from flask import session, redirect, url_for, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

ALLOWED_EXTENSIONS = {
    'imagem_produto': {'jpg', 'jpeg', 'png'},
    'arquivo_registro': {'pdf', 'doc', 'docx'},
    'arquivo_ficha_parecer': {'pdf', 'doc', 'docx'},
    'edital_pre_qualificacao': {'pdf', 'doc', 'docx'}
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(field, filename):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS.get(field, set())

def gerar_nome_unico(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    return f"{uuid.uuid4().hex}.{ext}"


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('perfil') != 'admin':
            flash('Acesso restrito. Esta funcionalidade é exclusiva para administradores.')
            return redirect(url_for('auth.home'))  # ou outra página padrão
        return f(*args, **kwargs)
    return decorated_function

limiter = Limiter(key_func=get_remote_address)

