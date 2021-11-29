FROM nikolaik/python-nodejs:python3.9-nodejs16
RUN apt-get update
RUN apt-get install -y jq
RUN npm install -g aws-cdk@1.134.0
RUN pip3 install checkov==2.0.603
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
unzip awscliv2.zip && ./aws/install
RUN wget https://releases.hashicorp.com/terraform/1.0.11/terraform_1.0.11_linux_amd64.zip && \
unzip terraform_1.0.11_linux_amd64.zip && rm terraform_1.0.11_linux_amd64.zip && \
mv terraform /usr/local/bin/terraform
RUN wget https://github.com/fugue/regula/releases/download/v2.1.0/regula_2.1.0_Linux_x86_64.tar.gz && tar -xvf regula_2.1.0_Linux_x86_64.tar.gz && rm -rf regula_2.1.0_Linux_x86_64.tar.gz
RUN mv regula /usr/local/bin/regula
RUN chmod +x /usr/local/bin/regula
ADD cfn-guard-linux /usr/local/bin/cfn-guard
RUN chmod +x /usr/local/bin/cfn-guard
ADD requirements.txt .
RUN pip3 install -r requirements.txt