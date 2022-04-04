Un data pipeline permettant d'ingérer des fichiers csv et json dans des table d'un dataset bigquery.
Une cloud function se charge de lire le fichier et le charge dans une table du dataset raw dans bigquery

Pour utiliser ce code vous devez disposer: 
- d'un compte gcp
- d'un compte github

***Attention ne pas créer au préalable un projet sur la plateforme gcp. Le script terraform se charge de créer le projet et les ressources nécessaires***

Utiliser le code :

En local créer un environnement virtuel
`python3 -m venv pdl_env` avec pdl_env un exemple de nom d'environnement

clonez ensuite le projet sur github
`git clone https://github.com/konan-cyrille/proj-data-lambda.git`

Allez à la racine du dossier cloné,
`cd proj-data-lambda`

Dans le dossier conf, edité le fichier ***.env.local*** avec votre éditeur de code préféré,
**env_name=[nom environnement]** qui peut prendre les valeurs dev, rec ou prod par exemple
**project_id=[id du projet gcp]**
**region=europe-west1**
**cloud_function_name=func-pdl**

Dépuis la racine du dossier exécuté le script ***./shell_scripts/setup_cloud_workspace.sh*** pour créer le projet et les ressources.

Une fois le projet crée allez sur [cloud console](https://console.cloud.google.com/)

Vérifier que le projet et les ressources ont étés crées avec succès.

###Quelques configuration manuelles avant de tester le projet