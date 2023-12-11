FROM ubuntu:latest
LABEL authors="mariazyryanova"

ENTRYPOINT ["top", "-b"]