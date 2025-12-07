FROM python:3.11-slim

WORKDIR /app

# Install APKTool and dependencies
RUN apt-get update && apt-get install -y \
    default-jre \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install APKTool
RUN wget https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool \
    && chmod +x apktool \
    && mv apktool /usr/local/bin/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]