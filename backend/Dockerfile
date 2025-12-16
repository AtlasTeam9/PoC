# Usa un'immagine leggera di Python
FROM python:3.11-slim

# Imposta la cartella di lavoro dentro il container
WORKDIR /app

# Copia il file dei requisiti e installa le librerie
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il codice del backend dentro il container
COPY . .

# Il comando per avviare il server (nota: host 0.0.0.0 è fondamentale per Docker)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]