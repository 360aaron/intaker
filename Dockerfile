FROM public.ecr.aws/lambda/python:3.12

ENV PIP_NO_CACHE_DIR=1

COPY requirements.txt edge.py lambda.py ./

RUN pip install -r requirements.txt
