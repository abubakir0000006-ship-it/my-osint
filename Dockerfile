FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y wget && \
    wget https://github.com/sundowndev/phoneinfoga/releases/latest/download/phoneinfoga_Linux_x86_64.tar.gz && \
    tar -xzf phoneinfoga_Linux_x86_64.tar.gz && \
    mv phoneinfoga /usr/local/bin/ && \
    rm phoneinfoga_Linux_x86_64.tar.gz

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
