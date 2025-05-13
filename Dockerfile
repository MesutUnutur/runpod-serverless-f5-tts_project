FROM pytorch/pytorch:2.4.0-cuda12.4-cudnn9-devel

USER root

ARG DEBIAN_FRONTEND=noninteractive

LABEL github_repo="https://github.com/SWivid/F5-TTS"

RUN set -x \
    && apt-get update \
    && apt-get -y install wget curl man git less openssl libssl-dev unzip unar build-essential aria2 tmux vim \
    && apt-get install -y openssh-server sox libsox-fmt-all libsox-fmt-mp3 libsndfile1-dev ffmpeg \
    && apt-get install -y librdmacm1 libibumad3 librdmacm-dev libibverbs1 libibverbs-dev ibverbs-utils ibverbs-providers \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean
    
WORKDIR /workspace

RUN git clone https://github.com/SWivid/F5-TTS.git \
    && cd F5-TTS \
    && git submodule update --init --recursive \
    && pip install -e . --no-cache-dir

RUN pip install runpod
RUN pip install ffmpeg-python==0.2.0
RUN pip install boto3==1.38.13
RUN pip install python-dotenv==1.1.0

WORKDIR /workspace/F5-TTS

COPY src/f5_tts/handler.py src/f5_tts/handler.py
COPY src/f5_tts/video_generate_from_voice_and_jpg.py src/f5_tts/video_generate_from_voice_and_jpg.py
COPY src/f5_tts/elon_musk_image.jpg src/f5_tts/elon_musk_image.jpg

VOLUME /root/.cache/huggingface/hub/

EXPOSE 7860 

CMD [ "python","src/f5_tts/handler.py" ]