FROM python:3.7-stretch
RUN apt-get update -y
COPY . app/
RUN pip3 install -r /app/requirements.txt
WORKDIR /app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]




