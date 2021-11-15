FROM nikolaik/python-nodejs:python3.9-nodejs14
RUN apt-get update
RUN apt-get install -y jq
RUN npm install -g aws-cdk
RUN pip3 install checkov
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
unzip awscliv2.zip && ./aws/install
ADD cfn-guard-linux /usr/local/bin/cfn-guard
RUN chmod +x /usr/local/bin/cfn-guard
ADD regula-linux /usr/local/bin/regula
RUN chmod +x /usr/local/bin/regula
ADD requirements.txt .
RUN pip3 install -r requirements.txt
