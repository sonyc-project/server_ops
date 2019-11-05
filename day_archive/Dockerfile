# docker build --no-cache -t sonyc_day_archive:0.1 .
# docker run -d -v /mount/vida-sonyc:/mount/vida-sonyc -it sonyc_day_archive:0.1
# docker run -d -v /Users/cm3580/dev/sonyc/sonycserver/operational/mount/vida-sonyc:/mount/vida-sonyc -it sonyc_day_archive:0.1 --data_folder /mount/vida-sonyc --time_since_dir_mod 48

FROM alpine:3.9
MAINTAINER Charlie Mydlarz (cmydlarz@nyu.edu)

ENV PYTHONUNBUFFERED=1

RUN echo "**** install Python ****" && \
    apk add --no-cache python3 && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi

RUN echo "**** copying server code to image ****"
COPY ./src /ops_code/day_archive/

ENTRYPOINT ["python", "/ops_code/day_archive/create_day_tar.py"]