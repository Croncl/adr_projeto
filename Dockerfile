FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Use o formato shell para expandir a variável $PORT corretamente
CMD gunicorn -b 0.0.0.0:$PORT main:app

#CMD ["python", "main.py"]
