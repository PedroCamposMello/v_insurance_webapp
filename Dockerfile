# Imagem base leve com Python 3.11
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Copiar dependências primeiro (cache mais eficiente)
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código
COPY . .

# Definir variável de ambiente da porta
ENV PORT=8000

# Expor porta (Back4App vai mapear automaticamente)
EXPOSE 8000

# Definir entrypoint (Flask app em handler.py → variável app)
# Gunicorn deve estar no requirements.txt
CMD ["gunicorn", "handler:app", "-b", "0.0.0.0:${PORT}"]