FROM python:3
#Install git
RUN mkdir /home/github && cd /home/github && git clone https://github.com/yenba/fredmiranda-post-upload-docker.git
#Set working directory
WORKDIR /home/github/fredmiranda-post-upload-docker
RUN pip install -r requirements.txt
ENTRYPOINT [ "python", "app.py" ]