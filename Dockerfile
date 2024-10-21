FROM python:3.13.0-alpine@sha256:c38ead8bcf521573dad837d7ecfdebbc87792202e89953ba8b2b83a9c5a520b6

ENTRYPOINT [ "/usr/local/bin/cfn-sync" ]

COPY requirements.txt /tmp/
RUN set -xe && \
  pip install --no-cache-dir -r /tmp/requirements.txt && \
  true

WORKDIR /cwd

ARG CFN_SYNC_VERSION
RUN set -xe && \
  pip install --no-cache-dir cfn-sync==${CFN_SYNC_VERSION} && \
  true
