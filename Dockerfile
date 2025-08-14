FROM python:3.14.0rc1-alpine@sha256:b0cfd0b2234c48a78d5ee6c7b082583a0c654317a6b0f03466db18ddd73b4fd6

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
