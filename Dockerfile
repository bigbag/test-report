FROM python:3.9.7

ARG USER_NAME="user"
ARG USER_HOME="/${USER_NAME}"
ARG APP_HOME="${USER_HOME}"

COPY poetry.lock pyproject.toml /

RUN apt-get update && \
    pip install --no-cache-dir --upgrade pip 'poetry>=1.0.0' && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-dev && \
    apt-get autoremove --purge -qy && \
    apt-get clean && \
    rm -rf /var/cache/* /poetry.lock /pyproject.toml

### Create service user ###
RUN groupadd -g 10001 ${USER_NAME} && useradd -g 10001 -u 10001 -md ${USER_HOME} ${USER_NAME}

### Add application source code ###
COPY docker-entrypoint.sh /usr/local/bin
COPY Makefile ${USER_HOME}
COPY --chown=10001:10001 app/ ${APP_HOME}/app

ENV PYTHONPATH="${APP_HOME}"

USER ${USER_NAME}
WORKDIR ${APP_HOME}
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["help"]
