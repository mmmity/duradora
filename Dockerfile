FROM python:3.12-alpine
RUN adduser -D duradora
USER duradora
WORKDIR /home/duradora
COPY src src
COPY tests tests
COPY duradora.py duradora.py
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8080
CMD python -m uvicorn duradora:app --host 0.0.0.0 --port 8080
