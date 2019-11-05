# docker build --no-cache -t sonyc_ops:0.1 .
# docker run -d -v /var/sonyc/datacache:/var/sonyc/datacache -v /mount/vida-sonyc:/mount/vida-sonyc -it sonyc_ops:0.1 --cache_folder /var/sonyc/datacache --out_folder /mount/vida-sonyc

# docker run -d -v /Users/cm3580/dev/sonyc/sonycserver/operational/var/sonyc/datacache:/var/sonyc/datacache -v /Users/cm3580/dev/sonyc/sonycserver/operational/mount/vida-sonyc:/mount/vida-sonyc -it sonyc_data_move:0.1 

FROM alpine:3.9
MAINTAINER Charlie Mydlarz (cmydlarz@nyu.edu)

ENV PYTHONUNBUFFERED=1

RUN echo "**** install Python ****" && \
    apk add --no-cache python3 && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi

RUN echo "**** copying server code to image ****"
COPY ./src /ops_code/