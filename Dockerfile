FROM ubuntu:latest
LABEL authors="Andres"

ENTRYPOINT ["top", "-b"]