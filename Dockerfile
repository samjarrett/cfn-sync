FROM python:3.11.0-alpine@sha256:672fe7da2dc85c8a2736870b23d848d02aa86a8d6bc2d3e6514fcb24beb06051

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
