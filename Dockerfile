FROM python:3
#Setup the variables
ENV DBNAME="DBNAMEHERE"
ENV DBUSER="DBUSERHERE"
ENV DBPASS="DBPASSHERE"
ENV DBHOST="DBHOSTHERE"
#Install git
RUN mkdir /home/github && cd /home/github && git clone https://github.com/yenba/fredmiranda-post-upload-docker.git
#Set working directory
WORKDIR /home/github/fredmiranda-post-upload-docker
RUN pip install -r requirements.txt && /usr/local/bin/python -m pip install --upgrade pip
CMD python app.py --dbname $DBNAME --dbuser $DBUSER --dbpass $DBPASS --dbhost $DBHOST