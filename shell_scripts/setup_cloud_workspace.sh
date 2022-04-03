#!/bin/bash

echo "Debut configuration de l'environnement cloud"
#gcloud auth application-default login

# On se place dans le dossier ou ce trouve ce fichier, 
# et on assigne à la variable DIR la la valeur de command pwd
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# initialisation d'une variable root_path avec la sortie de la commande pwd
root_path="$DIR/.."

# Rendre les variables d'environnement disponible
source "$root_path/conf/.env.local"
echo "Variable"
# echo "$(cat "${DIR}/conf/.env.local")"
echo ${PROJECT_ID}
echo ${ENVIRONMENT}

if [ -d "$root_path/src" ]; then
    # sudo apt-get install zip -y
    echo "suppression du fichier code.zip"
    rm $root_path/src/code.zip
    echo "Compression du contenu du dossier src"
    cd $root_path/src/flat_file_ingestor
    zip -r "../code.zip" .
    cd $root_path
fi;

if [ -d "$root_path/terraform_sripts" ]; then
    pwd
    echo "changement du repertoire courant de travail.."
    cd $root_path/terraform_sripts
    pwd
    # si le dossier qui port le nom de l'environnement n'existe pas, crée lé,
    if [ ! -d "$root_path/terraform_sripts/${ENVIRONMENT}/${PROJECT_ID}-${ENVIRONMENT}" ]; then
        echo "Le projet n'existe pas, Nous procédons a sa création..."
        # crée le dossier
        mkdir -p "$root_path/terraform_sripts/${ENVIRONMENT}/${PROJECT_ID}-${ENVIRONMENT}"
        # copie les fichiers main et variables le dossier
        cp main.tf variables.tf "${ENVIRONMENT}/${PROJECT_ID}-${ENVIRONMENT}/"
        cd "$root_path/terraform_sripts/${ENVIRONMENT}/${PROJECT_ID}-${ENVIRONMENT}"
        # exécute le main.tf pour créer les ressource dans le cloud
        terraform init
        terraform apply -auto-approve
        # # remet toi a la racine du projet
        # cd $root_path
    else
        echo "Le projet existe deja, Nous procédons a sa Mise à jour..."
        # copie les fichiers main et variables le dossier
        cp main.tf variables.tf "${ENVIRONMENT}/${PROJECT_ID}-${ENVIRONMENT}"
        cd "$root_path/terraform_sripts/${ENVIRONMENT}/${PROJECT_ID}-${ENVIRONMENT}"
        # exécute le main.tf pour créer les ressource dans le cloud
        terraform apply -auto-approve
        # # remet toi a la racine du projet
        # cd $root_path
    fi;
    # terraform apply -var project_name=${PROJECT_ID} -var env_name=${ENVIRONMENT} -auto-approve
    # terraform apply -auto-approve
    cd $root_path
fi

echo $PWD

echo 'FIN'
