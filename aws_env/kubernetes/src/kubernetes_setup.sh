#!/bin/bash

# 環境変数として情報を取得
HOSTZONE_ID=$(aws route53 list-hosted-zones --query "HostedZones[].Id" --output text | sed 's|/hostedzone/||g')
VPC_ID=$(aws ec2 describe-vpcs --query "Vpcs[].VpcId" --output text)
export HOSTZONE_ID VPC_ID BUCKET_NAME

# S3 CSIドライバーをインストール
helm repo add aws-mountpoint-s3-csi-driver https://awslabs.github.io/mountpoint-s3-csi-driver

# aws load balancer controllerをインストール
helm repo add eks https://aws.github.io/eks-charts

# update
helm repo update

# Helmを用いてデプロイ
## setup
helm upgrade --install setup ./setup \
   -n my-app \
   --create-namespace \
   --set region=$REGION \
   --set account_id=$ACCOUNT_ID \
   --set dns.domain=$DOMAIN \
   --set dns.owner_id=$HOSTZONE_ID \
   --set deployment.repository=api \
   --set deployment.service_account_name="cluster-role" \
   --set deployment.tag=api \
   --set volume.bucket_name=$BUCKET_NAME

## aws loadbalancer controllerのデプロイ
helm upgrade --install aws-load-balancer-controller \
   eks/aws-load-balancer-controller \
   -n kube-system \
   --set serviceAccount.create=false \
   --set serviceAccount.name=aws-load-balancer-controller \
   --set region=$REGION \
   --set clusterName="my-cluster" \
   --set vpcId=$VPC_ID

## aws s3 controllerのデプロイ
helm upgrade --install aws-mountpoint-s3-csi-driver \
   aws-mountpoint-s3-csi-driver/aws-mountpoint-s3-csi-driver \
   -n kube-system \
   --set controller.serviceAccount.create=false \
   --set node.serviceAccount.name=s3-controller \
   --set node.serviceAccount.create=false \
   --set clusterName="my-cluster" \
   --set region=$REGION \
   --set vpcId=$VPC_ID \
   --set node.tolerations[0].key=nvidia.com/gpu \
   --set node.tolerations[0].operator=Equal \
   --set node.tolerations[0].value=present \
   --set node.tolerations[0].effect=NoSchedule