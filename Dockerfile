FROM ubuntu:20.04

WORKDIR /app
COPY . .

RUN apt update && apt install python3 -y
RUN pip install -r requirements.txt

CMD ["python3","app.py"]