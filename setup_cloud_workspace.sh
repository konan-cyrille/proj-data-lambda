#!/bin/bash

echo "Debut configuration de l'environnement cloud"
#gcloud auth application-default login

# initialisation d'une variable root_path avec la sortie de la commande pwd
root_path=$(pwd)
echo $root_path

kern_name=$(uname -r)
echo $kern_name

if [ -d "$root_path/src" ]; then
    # sudo apt-get install zip -y
    echo "suppression du fichier code.zip"
    rm $root_path/src/code.zip
    echo "Compression du contenu du dossier src"
    zip -r "$root_path/src/code.zip" $root_path/src
fi;

if [ -d "$root_path/terraform_sripts" ]; then
    pwd
    echo "changement du repertoire courant de travail.."
    cd $root_path/terraform_sripts
    pwd
    # terraform init
    # terraform plan -var project_name="pdl-032022" -var env_name="dev"
    terraform apply -var project_name="pdl-032022" -var env_name="dev" -auto-approve
    cd $root_path
fi

echo $PWD
echo 'FIN'
