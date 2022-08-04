FROM python:3.11.0b5-alpine@sha256:f73caeb0970af18d51e1a5604c7cfae80c9067f9de377108f07a69182ef54468

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
