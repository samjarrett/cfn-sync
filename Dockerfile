FROM python:3.11.0b1-alpine@sha256:a6c232d42de9cea47ef5d3d5ca00acef42f7dfb9bd86f3051dff1fa3bb8d3ca5

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
