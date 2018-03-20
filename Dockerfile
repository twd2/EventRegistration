FROM ubuntu:latest
COPY . /tmp/er/
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6 && \
    echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-3.4.list && \
    apt-get update && \
    apt-get install -y \
            curl \
            git \
            python3 \
            python3-pip \
            python3-dev \
            mongodb-org \
            nginx && \
    curl -sL https://deb.nodesource.com/setup_8.x | bash - && \
    apt-get install -y nodejs && \
    apt-get autoremove -y && \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install -r /tmp/er/requirements.txt && \
    cat /etc/mongod.conf && \
    cp -f /tmp/er/conf/mongod.conf /etc/ && \
    rm -rf /tmp/er && \
    mkdir -p /data/mongodb && \
    chown mongodb:mongodb /data/mongodb && \
    mkdir -p /data/log/mongodb && \
    chown mongodb:mongodb /data/log/mongodb && \
    mkdir -p /data/nginx && \
    chown www-data:www-data /data/nginx && \
    mkdir -p /data/log/nginx && \
    chown www-data:www-data /data/log/nginx && \
    mkdir -p /data/er && \
    chown www-data:www-data /data/er
CMD bash
