#
# To build and run this container:
#
# docker build . -t dns-tool && docker run -it -v $(pwd):/mnt dns-tool
#
#
FROM alpine

WORKDIR /app

RUN apk add --no-cache python3 git

ADD dns-tool /app/dns-tool
ADD lib/ /app/lib/

RUN pip3 install git+https://github.com/dmuth/dns-tool/

ADD docker-entrypoint.sh /app/

ENTRYPOINT [ "/app/docker-entrypoint.sh" ]

