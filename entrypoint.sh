#!/bin/sh

# Espera o banco ficar acessível via TCP
echo "Aguardando MySQL subir (com wait-for-it)..."
/app/wait-for-it.sh db:3306 --timeout=60 --strict -- echo "MySQL está pronto, iniciando aplicação..."

# Inicia a aplicação
exec python app.py
