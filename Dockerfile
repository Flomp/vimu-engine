FROM python:3.10

RUN mkdir -p /usr/src/vimu-engine
WORKDIR /usr/src/vimu-engine

COPY . /usr/src/vimu-engine

RUN pip install --no-cache-dir --upgrade -r /usr/src/vimu-engine/requirements.txt

EXPOSE 5000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]