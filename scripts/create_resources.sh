#!/bin/bash

# Create GCS Bucket
gsutil mb -p <PROJECT_ID> -l <REGION> gs://airline-data-ingestion/

# Upload Data Files
gsutil cp ../data/airport_codes.csv gs://airline-data-ingestion/dimensional-data/
gsutil cp ../data/sample_flights.csv gs://airline-data-ingestion/daily-flight-data/

# Create Pub/Sub Topic
gcloud pubsub topics create gcs-file-uploads

# Create BigQuery Dataset
bq mk --dataset <PROJECT_ID>:airline_data

# Load Static Airport Data into BigQuery
bq load --source_format=CSV --skip_leading_rows=1 airline_data.airport_dim \
  gs://airline-data-ingestion/dimensional-data/airport_codes.csv ../schemas/airport_schema.json

# Create BigQuery Flight Table Schema
bq mk --table <PROJECT_ID>:airline_data.flight_fact \
  Carrier:STRING,OriginAirportID:INTEGER,OriginCity:STRING,OriginState:STRING,DestAirportID:INTEGER,DestCity:STRING,DestState:STRING,DepDelay:INTEGER,ArrDelay:INTEGER