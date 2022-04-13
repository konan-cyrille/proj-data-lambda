# Un projet crée via terraform n'a pas automatiquement de compte de facturation associé,
# il faut donc préciser un compte de facturation
data "google_billing_account" "acct" {
  display_name = "Mon compte de facturation"
  open         = true
}

###################################### LES RESSOURCES ###############################################
# creation du projet
resource "google_project" "project" {
  name       = "${var.project_name}-${var.env_name}"
  project_id = "${var.project_name}-${var.env_name}"

  billing_account = data.google_billing_account.acct.id
}

resource "google_project_service" "service" {
  for_each = toset([
    "compute.googleapis.com",
    "bigquery.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudfunctions.googleapis.com"
  ])
  service = each.key
  project            = google_project.project.project_id
  disable_on_destroy = true
}

output "project_id" {
  value = google_project.project.project_id
}


###### Ressource GCS #######
# Creation d'une ressource bucket qui contiendra les différents fichier
resource "google_storage_bucket" "bucket-auto-expire-in" {
  name          = "bkt-${google_project.project.project_id}-in"
  project       = google_project.project.project_id
  location      = "europe-west1"
  force_destroy = true

  # au bout de combien de jour le bucket sera detruit (au bout de 15J)
  # commenter le bloc lifecycle_rule si on ne veut pas que le bucket soit supprimé
  lifecycle_rule {
    condition {
      age = 15
    }
    action {
      type = "Delete"
    }
  }
}

# au bout de combien de jour le bucket sera detruit (au bout de 15J)
# commenter le bloc lifecycle_rule si on ne veut pas que le bucket soit supprimé
resource "google_storage_bucket" "bucket-auto-expire-handled" {
  name          = "bkt-${google_project.project.project_id}-handled"
  project       = google_project.project.project_id
  location      = "europe-west1"
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 15
    }
    action {
      type = "Delete"
    }
  }
}


# creation d'un objet dans le bucket
resource "google_storage_bucket_object" "archive" {
  name   = "archive/"
  source = "../../../README.md"
  bucket = google_storage_bucket.bucket-auto-expire-handled.name
}

# creation d'un objet dans le bucket
resource "google_storage_bucket_object" "rejet" {
  name   = "rejet/"
  bucket = google_storage_bucket.bucket-auto-expire-handled.name
  content = "rejet.txt"
}

# creation d'un objet dans le bucket
resource "google_storage_bucket_object" "in" {
  name   = "in/"
  bucket = google_storage_bucket.bucket-auto-expire-handled.name
  content = "in.txt"
}

# creation d'un objet dans le bucket
resource "google_storage_bucket_object" "output" {
  name   = "output/"
  bucket = google_storage_bucket.bucket-auto-expire-handled.name
  content = "output.txt"
}

###### Ressource Bigquery #######
# creation d'un dataset
resource "google_bigquery_dataset" "dataset_raw" {
  project       = google_project.project.project_id
  dataset_id                  = "raw"
  friendly_name               = "raw"
  description                 = "le dataset de l'environnement de dev"
  location                    = "europe-west1"

  # Attendre que toutes les api soit active
  depends_on = [google_project_service.service]
}

# creation d'un dataset
resource "google_bigquery_dataset" "dataset_prepared" {
  project       = google_project.project.project_id
  dataset_id                  = "prepared"
  description                 = "le dataset de l'environnement de dev"
  location                    = "europe-west1"

  # Attendre que toutes les api soit active
  depends_on = [google_project_service.service]
}

# creation d'un dataset
resource "google_bigquery_dataset" "dataset_sl_viz" {
  project       = google_project.project.project_id
  dataset_id                  = "sl_viz"
  description                 = "le dataset de l'environnement de dev"
  location                    = "europe-west1"

  # Attendre que toutes les api soit active
  depends_on = [google_project_service.service]
}


###### Ressource Cloud function  #######
# resource "google_cloudfunctions_function" "function_pdl" {
#   project       = google_project.project.project_id
#   name        = "func-pdl"
#   description = "Trigger when file object is created in the bucket source"
#   runtime     = "python38"
#   region      = "europe-west1"

#   event_trigger {
#       event_type = "google.storage.object.finalize"
#       resource = google_storage_bucket.bucket-auto-expire-in.name
#   }

#   available_memory_mb   = 512
#   source_archive_bucket = google_storage_bucket.bucket-auto-expire-handled.name
#   source_archive_object = google_storage_bucket_object.source_code.name

#   environment_variables = {
#     PROJECT_ID = google_project.project.project_id
#     BUCKET_NAME_IN  = google_storage_bucket.bucket-auto-expire-in.name
#     BUCKET_NAME_HANDLED = google_storage_bucket.bucket-auto-expire-handled.name
#   }
  
#   entry_point           = "process"
# }