data "terraform_remote_state" "aws_k8s_deployment" {
  backend = var.src.backend
  config  = try(local.config, {})
}
