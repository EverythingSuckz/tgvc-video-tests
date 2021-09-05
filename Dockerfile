FROM python:latest
RUN apt-get update && apt-get upgrade -y
RUN apt-get install python3-pip ffmpeg -y
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs
RUN npm i -g npm
WORKDIR /app
COPY . /app
RUN python3.9 -m pip install --upgrade pip
RUN python3.9 -m pip install -U -r requirements.txt
CMD python3.9 -m vcbot
