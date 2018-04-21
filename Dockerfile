#
# To build and run this container:
#
# docker build . -t dns-tool && docker run -it -v $(pwd):/mnt dns-tool
#
#
FROM alpine

RUN apk update

RUN apk add python3 git

RUN pip3 install git+https://github.com/dmuth/dns-tool/

ENTRYPOINT [ "/mnt/docker-entrypoint.sh" ]

