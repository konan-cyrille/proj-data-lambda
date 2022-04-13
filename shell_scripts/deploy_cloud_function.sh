#! /bin/bash

# On se place dans le dossier ou ce trouve ce fichier, 
# et on assigne à la variable DIR la la valeur de command pwd
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# on crée une variable contenant le chemin du dussier flat_file_ingestor
SOURCE_DIR="${DIR}/../src/flat_file_ingestor"

source "${DIR}/../conf/.env.local"

# gcloud config list
# gcloud auth application-default login #--no-browser
# gcloud config set project ${PROJECT_ID}
# gcloud config list

echo "Deployement de la cloud function..."
gcloud functions \
    deploy ${FUNCTION_NAME} \
    --project="${PROJECT_ID}-${ENVIRONMENT}" \
    --region=${PROJECT_REGION} \
    --entry-point=${cloud_function_entry_point}\
    --trigger-bucket=${BUCKET_TO_WATCH} \
    --runtime=python38 \
    --source=$SOURCE_DIR