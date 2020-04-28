FROM gcr.io/nectar-bazaar/py-ci:latest

WORKDIR /app

ADD Pipfile Pipfile.lock ./
RUN pip3 install pipenv
RUN pipenv install

ADD . /app

ENTRYPOINT ["/py-ci/start.sh"]