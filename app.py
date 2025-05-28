from flask import Flask, render_template
from routes.auth_routes import bp_auth
from routes.marcas_routes import bp_marcas
from routes.public_routes import bp_public
from routes.catalogo_routes import bp_catalogo
from routes.export_routes import bp_export
from datetime import timedelta
import os
from flask_talisman import Talisman
from utils.helpers import limiter, MAX_FILE_SIZE
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).resolve().parent / '.env') 


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret')
Talisman(app, content_security_policy=None)
#app.permanent_session_lifetime = timedelta(minutes=1)  # 30 minutos de inatividade

app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE  


# inicializa o limiter a partir da instância de extensions.py
limiter.init_app(app)
# (se quiser defaults globais, você pode passar default_limits aqui:
# limiter.init_app(app, default_limits=["200 per day", "50 per hour"])
# ou configurar por blueprint/rota como fizemos abaixo)

# Registro dos Blueprints
app.register_blueprint(bp_auth)
app.register_blueprint(bp_marcas)
app.register_blueprint(bp_catalogo)
app.register_blueprint(bp_export)
app.register_blueprint(bp_public)


@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template("erro_404.html"), 404

@app.errorhandler(500)
def erro_interno(e):
    return render_template("erro_500.html"), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


