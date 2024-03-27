FROM python:3

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /app/

COPY templates /app/templates/

EXPOSE 5000

ENTRYPOINT [ "gunicorn", "app:app", "-b", "0.0.0.0:5000"]
