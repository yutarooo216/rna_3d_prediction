# rna_3d_prediction
A Single Page Application (SPA) using AWS that predicts the 3D structure of RNA sequences and returns the result via email.

## Architecture Overview
- GPU nodes used for inference are managed with Kubernetes and support auto-scaling, which helps reduce GPU usage costs.
- All Kubernetes resources are managed using Helm.
- Results are returned to users via AWS Lambda triggered email.
- Infrastructure is managed using Terraform (IaC), and GitHub Actions is used for Continuous Deployment (CD).
- The frontend is built with React.

## Usage Instructions

### 1. Backend Environment Setup
Terraform, Kubernetes, and other backend components are containerized and run via Docker:
```bash
# Start Docker containers
$ cd ./aws_env/docker
$ docker compose up -d

# Link your AWS account
$ docker compose exec -e COLUMNS=$COLUMNS aws bash
$ aws configure
```

### 2. Backend Setup
Set your custom S3 buckets as environment variables. Replace the following with your own bucket names:
```bash
# S3 bucket settings for backend
$ BACKEND_BUCKET=my-terraform-backend-bucket-name     # for Terraform backend
$ BUCKET_NAME=rna-3d-predictions                      # for storing RNA prediction results
```
Now, set up the backend infrastructure using the following steps:
```bash
# Deploy AWS infrastructure with Terraform
$ cd ./aws_env/terraform
$ source terraform_setup.sh

# Set up EKS cluster
$ cd ./aws_env/kubernetes
$ source ./src/eks_setup.sh

# Deploy Kubernetes resources
$ source ./src/kubernetes_setup.sh
```
You can test the backend using:
```bash
$ curl -X POST http://$DOMAIN/submit-job/ \
  -H "Content-Type: application/json" \
  -d '{
  "sequence": "AUGCUUAGCUGA",
  "email": "user@example.com"  # Replace with your actual email for testing
  }'
```

### 3. Frontend Setup
After running the following commands, access the app via http://localhost:3000:
```bash
# Set up the frontend environment
$ cd ./rna-fronted
$ docker compose up -d
```
Enter your RNA sequence and email address, then click Submit to start the prediction.
  
![frontend_image](images/frontend_image.png)