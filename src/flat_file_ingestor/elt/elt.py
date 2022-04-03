import pandas as pd
# import logging
import traceback
import datetime as dt
import hashlib
import os

from google.cloud import bigquery
from google.cloud import storage



PROJECT_ID = os.getenv('PROJECT_ID')
BUCKET_NAME_IN  = os.getenv('BUCKET_NAME_IN')
BUCKET_NAME_HANDLED = os.getenv('BUCKET_NAME_HANDLED')


# logging.basicConfig(level=logging.INFO, filename='../logApp/elt.log', format='%(asctime)s:%(levelname)s:%(message)s')


def check_if_file_already_handled():
    pass

def read_blob_from_gcs(gcs_client, file_path, bucket_name=None):
    bucket = gcs_client.get_bucket(bucket_name)
    # obtention du contenue du bucket sous forme d'objet blob
    blob = bucket.get_blob(file_path)
    # convertion en string, le string obtenu est un object bytes
    content = blob.download_as_string()
    return content
    
def hash_blob(blob_as_string):
    """
    Cette fonction permet de hasher le contenu d'un blob
    arg:
        blob_as_string (bytes object): le contenu d'un blob sous forme d'objet bytes
    """
    # On crée un objet hash avec la librairie haslib, on peut utiliser d'autre algorithme de hashage autre que`.sha256()`
    file_hash = hashlib.sha256() 
    file_hash.update(blob_as_string)
    return file_hash.hexdigest()

# def hash_file(file_path, block_size=None):
#     """
#     Cette fonction permet de hasher le contenu d'un fichier
#     soit tout le contenu du fichier est hashé en une seule fois,
#     soit le hashage se fait par petit bout
#     arg:
#         file_path (str): le chemin du fichier
#         block_size (int): le nombre de bit à lire
#     """
#     # On crée un objet hash avec la librairie haslib, on peut utiliser d'autre algorithme de hashage autre que`.sha256()`
#     file_hash = hashlib.sha256() 
#     with open(file_path, 'rb') as f: # overture et lecture du fichier (binaire) dans un objet f
#         content = f.read(block_size) #o n lit un morceau des binaires de l'objet f
#         while len(content) > 0:
#             file_hash.update(content)
#             content = f.read(block_size)
#     return file_hash.hexdigest()


def make_metadata(gcs_client, file_path, status):
    """
    cette methode permet de générer des information, qui seront loguer dans une table
    args:
        file_path (str): le chemin du fichier
        status (str): L for Loaded or R for Rejected
    """
    now = dt.datetime.now()
    loaded_datetime = now.strftime("%d %m %Y %H:%M:%S")
    
    # lecture et hashage d'un objet blob
    d = read_blob_from_gcs(gcs_client, file_path=file_path, bucket_name=BUCKET_NAME_IN)
    h = hash_blob(d)
    
    meta_data = {"file_path":[file_path], "file_hash":[h], "file_status":[status], "loaded_datetime":[loaded_datetime]}
    df_metadata = pd.DataFrame(meta_data)
    # print(df_metadata.head())
    return df_metadata


def read_file(input_file_path):
    file_extension = input_file_path.split('.')[-1].strip().lower()
    try:
        if file_extension == 'csv':
            print(f"Lecture d'un fichier {file_extension}")
            df = pd.read_csv(input_file_path)
            print(f"Done!")
            return df
        if file_extension == 'json':
            print(f"Lecture d'un fichier {file_extension}")
            df = pd.read_json(input_file_path)
            print(f"Done!")
            return df
    except Exception as e:
        # print to sysout
        traceback.print_exc()


def load_to_bigquery(client, df, project_id, dataset_name, table_name, write_mode):
    """Charge les données d'un dataframe dans une table bigquery.
    Args:
         client (bigquery_client): un client bigquery.
         df (dataframe): un objet dataframe.
         dataset_name : le nom du dataset
         table_name : le nom de la table
         write_mode : comment les données sont écrite sur la table "WRITE_TRUNCATE" "WRITE_APPEND"
    """
    tbl_fullname = f"{project_id}.{dataset_name}.{table_name}"
    
    # configuration du job
    job_config = bigquery.LoadJobConfig(
        # Comment les données sont écrite dans la table
        write_disposition=write_mode,
    )

    job = client.load_table_from_dataframe(
        df, tbl_fullname, job_config=job_config
    )
    # faire une requête à l'API
    job.result()
    return job.done()



def move_blob(gcs_client, bck_name_src, bck_name_dst, blob_name_src, bucket_prefix='archive'):
    """
    Cette methode deplace un object soit dans le dossier archive soit le dossier rejeté dans un bucket
    args:
        gcs_client (object): un client cloud storage
        bck_name_src (str): le nom du bucket source
        bck_name_dst (str): le nom du bucket de destination
        blob_name_src (str): le nom du blob à deplacer le (nom_du_fichier.extension)
        bucket_prefix (str): designe un dossier dans un bucket (archive ou rejet)
    """
    # Instanciation des objets bucket source et object bucket destination
    obj_bck_src = gcs_client.bucket(bck_name_src)
    obj_bck_dst = gcs_client.bucket(bck_name_dst)
    # Instanciation d'un object blob à partir du nom du blob
    obj_blob_src = obj_bck_src.blob(blob_name_src)
    print(f"""Deplacement du blob {blob_name_src} dans le dossier {bucket_prefix} du bucket {bck_name_dst}...""")
    dst_blob_name = f"""{bucket_prefix}/{blob_name_src}-{dt.datetime.now().strftime("%d%m%Y%H%m%s")}"""
    # Copy du blob source depuis le bucket source ver le bucket de destination
    blob_copy = obj_bck_src.copy_blob(
        obj_blob_src, obj_bck_dst, dst_blob_name
    )
    # Suppression du blob source
    obj_bck_src.delete_blob(blob_name_src)
    print(f"Le blob {blob_name_src} à été déplacé avec succès et supprimé du bucket source : {bck_name_src}")
    return "done"


def run(file_path, gcs_client, bq_client):
    print(f"Debut du traitement fichier {file_path}")
    file_with_extension = file_path.split('/')[-1]
    fileName_without_extension = file_path.split('.')[0]
    file_path_gs = f"gs://{BUCKET_NAME_IN }/{file_path}"
    try:
        df = read_file(file_path_gs)
        print(f"dataframe length: {len(df)}")
        ltb = load_to_bigquery(bq_client, df, project_id=PROJECT_ID, dataset_name='raw', table_name=fileName_without_extension, write_mode='WRITE_TRUNCATE')
        if ltb:
            status = 'L'
            df_metedata = make_metadata(gcs_client, file_path, status=status)
            load_to_bigquery(bq_client, df_metedata, project_id=PROJECT_ID, dataset_name='prepared', table_name="logs_file", write_mode='WRITE_APPEND')
            move_blob(gcs_client, bck_name_src=BUCKET_NAME_IN , bck_name_dst=BUCKET_NAME_HANDLED, blob_name_src=file_with_extension, bucket_prefix='archive')
    except:
        status = 'R'
        df_metedata = make_metadata(gcs_client, file_path, status=status)
        load_to_bigquery(bq_client, df_metedata, project_id=PROJECT_ID, dataset_name='prepared', table_name="logs_file", write_mode='WRITE_APPEND')
        move_blob(gcs_client, bck_name_src=BUCKET_NAME_IN , bck_name_dst=BUCKET_NAME_HANDLED, blob_name_src=file_with_extension, bucket_prefix='rejet')

if __name__ == '__main__':
    bq_client = bigquery.Client()
    gcs_client = storage.Client()
    run("drugs.csv", gcs_client, bq_client)
    # client = bigquery.Client()
    # fileName_without_extension = 'drugs'
    # lbq = load_to_bigquery(client, df, project_id=PROJECT_ID, dataset_name='raw', table_name=fileName_without_extension, write_mode='WRITE_TRUNCATE')
    # print(lbq)
    # d = read_blob_from_gcs(gcs_client, file_path="drugs.csv", bucket_name=BUCKET_NAME_IN)
    # print(d)
    # h = hash_blob(d)
    # print(h)
    
    pass

