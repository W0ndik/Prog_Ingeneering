FROM python:3.10-slim

ENV DATABASE_URL=postgresql://user:password@db:5432/mydatabase
RUN mkdir /app
WORKDIR /app
COPY /src /app/
COPY requirements.txt /app/
COPY openapi.json /app/
RUN pip install -q -r /app/requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]