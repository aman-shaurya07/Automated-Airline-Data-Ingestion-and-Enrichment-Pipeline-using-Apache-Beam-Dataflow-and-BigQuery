#!/bin/bash

# Delete GCS Bucket
gsutil rm -r gs://airline-data-ingestion/

# Delete Pub/Sub Topic
gcloud pubsub topics delete gcs-file-uploads

# Delete BigQuery Dataset
bq rm -r -f -d <PROJECT_ID>:airline_data