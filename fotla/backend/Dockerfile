FROM python:3.10

RUN apt-get update &&\
    apt-get -y install locales &&\
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm

RUN pip install --upgrade pip

# Poetryのインストール
RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.2.2

ENV PATH /root/.local/bin:$PATH

COPY ./ /usr/fotla

WORKDIR /usr/fotla

RUN poetry config virtualenvs.create false &&\
    ls -la &&\
    poetry install --no-dev --no-interaction
