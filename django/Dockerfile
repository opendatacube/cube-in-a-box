FROM osgeo/gdal:ubuntu-small-3.6.3

ENV DEBIAN_FRONTEND=noninteractive \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    TINI_VERSION=v0.19.0

# Adicionando Tini para um encerramento mais limpo
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

# Instalando dependências
RUN apt-get update && \
    apt-get install -y \
        libgdal-dev \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiando arquivos necessários
COPY requirements.txt .

# Instalando dependências do Python
RUN pip install --no-cache-dir -r requirements.txt


# Copiando o restante do código-fonte
COPY . .

# Expondo a porta 8000
EXPOSE 8000

# Definindo o comando de inicialização usando Tini
ENTRYPOINT ["/tini", "--"]

# Comando padrão para iniciar o Django e Gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn cuborizonte.wsgi:application -b 0.0.0.0:8000"]
