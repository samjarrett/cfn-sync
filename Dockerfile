FROM python:3.11.0a6-alpine@sha256:88cd3b8de639b03c52cb702c1bbeb4ec5f5e16ce55dc7a72ab3a4255d0dbcd43

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
