src = {
  backend    = "s3"
  config_key = "terraform/fintechless/ftl-msa-msg-out/aws_k8s_deployment/terraform.tfstate"

  msa            = "msg-out"
  container_port = 5003
}
