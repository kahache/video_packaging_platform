FROM python:3.6

COPY . /service/

RUN mkdir /service/storage /service/output

RUN pip3 install -r /service/app/requirements.txt

WORKDIR /service/app

EXPOSE 5000

EXPOSE 8080

CMD python3 app.py
