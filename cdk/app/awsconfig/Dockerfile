FROM public.ecr.aws/lambda/python:3.9

COPY ./cfn-guard /usr/local/bin
COPY S3_block_public_access.py requirements.txt install.sh ${LAMBDA_TASK_ROOT}/
COPY ./rules/ ${LAMBDA_TASK_ROOT}/rules/
WORKDIR ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt
RUN yum install -y jq tar gzip
RUN sh ./install.sh;cfn-guard -V
CMD [ "S3_block_public_access.lambda_handler" ]