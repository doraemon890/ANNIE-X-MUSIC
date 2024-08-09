FROM nikolaik/python-nodejs:python3.10-nodejs20

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . /app/
WORKDIR /app/

# Upgrade pip to the latest version
RUN pip3 install --no-cache-dir --upgrade pip

# Install dependencies
RUN pip3 install --no-cache-dir --upgrade --requirement requirements.txt

CMD bash start