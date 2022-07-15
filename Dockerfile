FROM python:3.11.0b4-alpine@sha256:f0fa7a1c441021a79cf4c3430bb02ebde95045e43221d44419032138bb541e4a

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
