from elt.elt import run
from google.cloud import bigquery
from google.cloud import storage

def process(event, context):
    """Se declenche par la création d'un object dans un bucket Cloud Storage.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Les metadonnée de l'Event.
    """
    bq_client = bigquery.Client()
    gcs_client = storage.Client()
    
    file_name = event['name']
    bucket_name = event['bucket']
    
    print(f"bucket handled: {bucket_name}.")
    print(f"Processing file: {file_name}.")
    
    run(file_name, gcs_client, bq_client)
    print("FIN")