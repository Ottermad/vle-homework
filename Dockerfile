FROM python:3.5
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
RUN pip install git+https://ottermad:af7e0fa5f87f3823703d9e58c7626f0fce6c8c41@github.com/Ottermad/vle-internals.git
RUN pip install git+https://ottermad:af7e0fa5f87f3823703d9e58c7626f0fce6c8c41@github.com/Ottermad/services_extension.git

ADD . /code/

CMD ["python", "manage.py","--config", "minikube", "run"]
