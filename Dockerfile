FROM python:3

WORKDIR /app

COPY app.py requirements.txt ./

COPY templates ./templates

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "python", "-m", "flask", "run", "--host=0.0.0.0" ]
