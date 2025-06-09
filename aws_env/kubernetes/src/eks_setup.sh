#!/bin/bash

# 環境変数の設定
SUBNET_ID_1A=$(aws ec2 describe-subnets --filters "Name=tag:Name,Values=eks-subnet-1a" --query "Subnets[0].SubnetId" --region ap-northeast-1 --output text)
SUBNET_ID_1C=$(aws ec2 describe-subnets --filters "Name=tag:Name,Values=eks-subnet-1c" --query "Subnets[0].SubnetId" --region ap-northeast-1 --output text)
ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
export SUBNET_ID_1A SUBNET_ID_1C ACCOUNT_ID

# templateからyamlを作成
envsubst < ./cluster/eks_cluster.yaml.template > ./cluster/eks_cluster.yaml

# クラスターの構築
eksctl create cluster -f ./cluster/eks_cluster.yaml