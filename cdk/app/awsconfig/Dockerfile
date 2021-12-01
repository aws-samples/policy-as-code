FROM public.ecr.aws/lambda/python:3.9

COPY S3_block_public_access.py requirements.txt install.sh ${LAMBDA_TASK_ROOT}/
COPY ./rules/ ${LAMBDA_TASK_ROOT}/rules/
WORKDIR ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt
RUN yum install -y jq tar gzip curl
RUN curl --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/dchakrav-github/cloudformation-guard/main/install-guard.sh | VERSION=v2.1.0-pre-rc1 sh
RUN cp ~/.guard/bin/cfn-guard /usr/local/bin
CMD [ "S3_block_public_access.lambda_handler" ]
