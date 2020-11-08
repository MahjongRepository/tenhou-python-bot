FROM pypy:3.7-7.3.2-slim

RUN useradd -ms /bin/bash docker-user

WORKDIR /app/

COPY requirements /requirements
RUN pip install --no-cache-dir -r /requirements/dev.txt

COPY ./project .

USER docker-user