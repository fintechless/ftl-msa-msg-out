data "terraform_remote_state" "aws_iam_eks_node_group" {
  backend = var.src.backend
  config  = try(local.config, {})
}
