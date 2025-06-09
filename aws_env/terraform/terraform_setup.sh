# 環境変数として情報を取得
DOMAIN=$(aws route53 list-hosted-zones --query "HostedZones[].Name" --output text | sed 's/\.$//')
REGION=$(aws configure get region)
export DOMAIN REGION BACKEND_BUKET

# .tfファイルの生成
envsubst < ./main.template > ./main.tf
envsubst < ./network.template > ./network.tf
envsubst < ./domain.template > ./domain.tf
envsubst < ./policy.template > ./policy.tf
envsubst < ./ses.template > ./ses.tf
envsubst < ./lambda.template > ./lambda.tf

# terraformの初期化と反映
terraform init
terraform apply