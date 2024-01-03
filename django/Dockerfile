# Use a imagem base Python
FROM python:3.10

# Defina o diretório de trabalho no contêiner
WORKDIR /app

# Copie os arquivos de requisitos para o diretório de trabalho
COPY requirements.txt .

# Instale as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante dos arquivos para o diretório de trabalho
COPY . .

# Expõe a porta 8000 para a aplicação Django
EXPOSE 8000

# Comando para iniciar o servidor Gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn cuborizonte.wsgi:application -b 0.0.0.0:8000"]
