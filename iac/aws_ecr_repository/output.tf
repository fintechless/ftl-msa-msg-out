output "repository_url" {
  value       = aws_ecr_repository.this[var.src[0]].repository_url
  description = "ECR repository URL."
}
