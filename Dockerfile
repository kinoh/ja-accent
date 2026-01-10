FROM debian:bookworm-slim AS build

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        g++ \
        make && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY packages/CRF++-0.58.tar.gz ./
RUN tar -xzf CRF++-0.58.tar.gz && \
    cd /app/CRF++-0.58 && \
    sh ./configure && \
    make && \
    make install && \
    cd /app && \
    rm -rf CRF++-0.58 CRF++-0.58.tar.gz

COPY packages/mecab-0.996.tar.gz ./
RUN tar -xzf mecab-0.996.tar.gz && \
    cd /app/mecab-0.996 && \
    ./configure && \
    make && \
    make install && \
    cd /app && \
    rm -rf mecab-0.996 mecab-0.996.tar.gz

FROM python:3.13-slim AS runtime

WORKDIR /usr/src/app

RUN apt-get update && \
    apt-get install -y --no-install-recommends unzip && \
    rm -rf /var/lib/apt/lists/*

COPY packages/unidic-csj-202512.zip ./
RUN unzip -q unidic-csj-202512.zip -d /usr/src/app/unidic && \
    rm unidic-csj-202512.zip

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ENV LD_LIBRARY_PATH="/usr/local/lib"

COPY --from=build /usr/local/bin/crf_test /usr/local/bin/
COPY --from=build /usr/local/bin/mecab /usr/local/bin/
COPY --from=build /usr/local/lib/libcrfpp.so* /usr/local/lib/
COPY --from=build /usr/local/lib/libmecab.so* /usr/local/lib/
COPY --from=build /usr/local/etc/mecabrc /usr/local/etc/mecabrc
COPY --from=build /usr/local/libexec/mecab/mecab-dict-index /usr/local/libexec/mecab/mecab-dict-index

COPY src/user.dic ./
COPY src/model_accent ./

COPY src/*.py .

ENV MECAB_DICDIR="/usr/src/app/unidic"
ENV MECAB_USERDIC="/usr/src/app/user.dic"

EXPOSE 2954

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "2954", "--no-access-log"]
