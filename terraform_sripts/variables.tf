variable "env_name" {
  type        = string
  description = "Le nom de l'environnement qui peut être dev, rec, prod"
  default = "dev"
}

variable "project_name" {
  type        = string
  description = "Le nom du projet à créer"
  default = "pdl-032022"
}