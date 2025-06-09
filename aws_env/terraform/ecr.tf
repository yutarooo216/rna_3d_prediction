resource "aws_ecr_repository" "gpu-repository" {
  name                 = "gpu-repository"
  image_tag_mutability = "MUTABLE" # イメージタグの変更が可能
}

resource "aws_ecr_repository" "api" {
  name                 = "api"
  image_tag_mutability = "MUTABLE" # イメージタグの変更が可能
}