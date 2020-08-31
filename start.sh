#!/bin/bash
app="docker.translate"
docker build -t ${app} .
docker run -d -p 8003:80 \
  --name=${app} \
  -v $PWD:/app ${app}