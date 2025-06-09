FROM python:3.13

ARG pip_installer="https://bootstrap.pypa.io/get-pip.py"
ARG awscli_version="1.16.236"

# install command.
RUN apt-get update && apt-get install -y less vim jq unzip sshpass wget curl sudo

# create local bin directory
RUN mkdir -p /root/.local/bin
ENV PATH $PATH:/root/.local/bin

# install aws-cli ver2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install

# install ecr helper
RUN apt-get install -y amazon-ecr-credential-helper

# install sam
RUN pip install --user --upgrade aws-sam-cli

# install eksctl 0.199.0
RUN curl --silent --location "https://github.com/eksctl-io/eksctl/releases/download/v0.199.0/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
RUN mv /tmp/eksctl /usr/local/bin
RUN eksctl version

# install kubectl 1.17.9
RUN curl -o kubectl https://amazon-eks.s3.us-west-2.amazonaws.com/1.17.9/2020-08-04/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin
RUN mkdir -p $HOME/bin && cp /usr/local/bin/kubectl $HOME/bin/kubectl && export PATH=$PATH:$HOME/bin
RUN echo 'export PATH=$PATH:$HOME/bin' >> ~/.bash_profile

# install Terraform v1.5.7
RUN wget https://releases.hashicorp.com/terraform/1.5.7/terraform_1.5.7_linux_amd64.zip
RUN unzip terraform_1.5.7_linux_amd64.zip
RUN mv terraform /usr/local/bin/
RUN terraform version

RUN aws --version
RUN kubectl version --short --client

RUN echo "alias ll='ls -al'" >> /root/.bashrc

RUN pip install ansible

RUN ansible-galaxy collection install community.kubernetes

# helm install
RUN curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
RUN chmod 700 get_helm.sh
RUN ./get_helm.sh

# kustomize install
RUN curl -s "https://api.github.com/repos/kubernetes-sigs/kustomize/releases/latest" | jq -r '.assets[] | select(.name | test("kustomize.*linux.*.tar.gz")) | .browser_download_url' | wget -i -
RUN tar -zxvf kustomize_v*.*.*_linux_amd64.tar.gz
RUN mv kustomize /usr/local/bin/
RUN rm kustomize_*

# user add
RUN groupadd -g 1000 user
RUN useradd -m -s /bin/bash -u 1000 -g 1000 user1

# docker soket
RUN usermod -aG docker user1

USER user1
WORKDIR /home/user1

USER root
