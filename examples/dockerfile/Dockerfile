FROM python:alpine3.14

RUN apk --update add --no-cache cargo
RUN cargo install cfn-guard
ENV PATH "/root/.cargo/bin:${PATH}"
RUN pip3 install cfn-lint