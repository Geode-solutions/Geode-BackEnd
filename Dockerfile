FROM python:3.9-slim-buster 

WORKDIR /server

COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3", "app.py"]

EXPOSE 5000