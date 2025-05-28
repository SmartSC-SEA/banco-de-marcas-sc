FROM python:3.12-slim

# Instala dependências de sistema necessárias para o mysqlclient e netcat
RUN apt-get update --allow-insecure-repositories \
 && apt-get install -y --allow-unauthenticated \
    build-essential \
    gcc \
    pkg-config \
    netcat-openbsd \
    default-libmysqlclient-dev \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# Copia o arquivo de dependências
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY . .

# Evita buffering nos logs do Python
ENV PYTHONUNBUFFERED=1
COPY wait-for-it.sh /app/wait-for-it.sh
# Entrypoint padrão (ajuste conforme sua aplicação)
ENTRYPOINT ["sh", "entrypoint.sh"]
