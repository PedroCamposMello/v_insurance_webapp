FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000
EXPOSE 8000

# CMD corrigido (expansão de variáveis agora funciona)
CMD ["sh", "-c", "gunicorn handler:app -b 0.0.0.0:$PORT"]