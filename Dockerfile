FROM python:3.13.3-slim

WORKDIR /app

# Instala dependências de sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos do projeto
COPY . .

# Instala dependências do projeto
RUN pip install --upgrade pip && pip install -r requirements.txt

# Comando padrão (pode ser sobrescrito)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
