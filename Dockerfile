# Base image
FROM ubuntu:16.04

# MAINTAINER
MAINTAINER test

# node run env
RUN \
    apt-get update && \
    apt-get install -y -q --no-install-recommends \
        autoconf cmake vim git libbz2-dev libdb++-dev libdb-dev libssl-dev openssl libreadline-dev libtool libcurl4-openssl-dev libboost-all-dev g++
    && apt-get clean 

WORKDIR /

VOLUME /temp

EXPOSE 8048
EXPOSE 8049
EXPOSE 8050

