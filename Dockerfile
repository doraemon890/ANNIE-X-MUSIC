FROM nikolaik/python-nodejs:python3.10-nodejs19

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . /app/
WORKDIR /app/

# Upgrade pip
RUN python3 -m pip install --no-cache-dir --upgrade pip

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

CMD bash start
