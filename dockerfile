#FROM nvidia/cuda:11.4.0-cudnn8-runtime-ubuntu20.04
FROM nvidia/cuda:11.4.0-base-ubuntu20.04

WORKDIR /bssoft
COPY . .

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul

RUN ["/bin/bash", "-c", "ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone"]

RUN apt-get update \
    && apt-get install -y net-tools \
    && apt-get install -y python3-pip \
    && apt-get install -y git \
    && apt-get install -y vim \
    && apt-get install -y libsndfile1-dev \
    && apt-get install -y ffmpeg \
    && pip3 --no-cache-dir install -r requirements.txt \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

CMD ["./run.sh"]
