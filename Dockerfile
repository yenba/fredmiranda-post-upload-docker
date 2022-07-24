FROM python:3
ADD requirements.txt /
RUN pip install -r requirements.txt
ADD app.py /
ADD pool_methods.py /
CMD [ "python", "./app.py" ]