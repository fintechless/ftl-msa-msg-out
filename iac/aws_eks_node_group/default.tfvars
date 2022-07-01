src = {
  backend    = "s3"
  config_key = "terraform/fintechless/ftl-msa-msg-out/aws_iam_eks_node_group/terraform.tfstate"

  node_group_name = "ftl-msa-msg-out-node-group"
  instance_types  = ["t3.micro"]
  ami_type        = "AL2_x86_64"

  scaling_config = {
    desired_size = 1
    max_size     = 25
    min_size     = 1
  }
}
