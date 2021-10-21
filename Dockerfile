FROM pypy:3.7-7.3.6-slim

RUN useradd -ms /bin/bash docker-user

WORKDIR /app/

RUN python3 -m pip install pip==21.3

COPY requirements /requirements
RUN pip install --no-cache-dir -r /requirements/dev.txt

COPY ./project .

USER docker-user