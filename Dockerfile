FROM ubuntu:14.04

ENV HOME /app

ADD http://download.macromedia.com/pub/developer/opentype/FDK-25-LINUX.zip /app/
RUN apt-get update -y && apt-get install -y cython fontforge python-fontforge git unzip python-pip libharfbuzz-dev libharfbuzz-bin libharfbuzz0b python-numpy python-scipy
WORKDIR /app
RUN git clone https://github.com/behdad/fonttools.git && \
    git clone https://github.com/robofab-developers/robofab.git && \
    git clone https://github.com/typesupply/feaTools.git && \
    git clone https://github.com/typemytype/booleanOperations.git && \
    git clone https://github.com/typesupply/ufo2fdk.git 

RUN /usr/bin/unzip /app/FDK-25-LINUX.zip

WORKDIR /app/fonttools
RUN python ./setup.py install

WORKDIR /app/robofab
RUN python ./setup.py install

WORKDIR /app/feaTools
RUN python ./setup.py install

WORKDIR /app/booleanOperations/cppWrapper
RUN python ./setup.py build 

WORKDIR /app/booleanOperations
RUN python ./setup.py install && cp cppWrapper/build/lib.linux-x86_64-2.7/pyClipper.so /usr/local/lib/python2.7/dist-packages/booleanOperations/pyClipper.so

WORKDIR /app/ufo2fdk
RUN python ./setup.py install

WORKDIR /app/src

ENDPOINT ["make"]
