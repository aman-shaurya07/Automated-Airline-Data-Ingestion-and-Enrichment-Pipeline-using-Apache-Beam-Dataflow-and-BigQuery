# Automated Airline Data Ingestion and Enrichment Pipeline using Apache Beam, Dataflow, and BigQuery

This project demonstrates an end-to-end data pipeline for processing and enriching daily flight data using Google Cloud Platform (GCP). The pipeline integrates static airport information with dynamic flight data and loads enriched data into BigQuery for analytics. The project is implemented using GCP CLI, Apache Beam (Dataflow), and GCP services.

---

## **Project Overview**

### **Objective**
To build a scalable and automated data pipeline that:
1. Processes daily flight data dynamically uploaded to Google Cloud Storage (GCS).
2. Enriches the flight data with static airport information (city, state).
3. Stores enriched data in BigQuery for analysis.

### **Tech Stack**
1. **Google Cloud Storage (GCS)**: For storing raw flight and airport data.
2. **Google Cloud Pub/Sub**: For triggering workflows on file uploads.
3. **BigQuery**: For schema detection and storing processed data.
4. **Dataflow (Apache Beam)**: For ETL (Extract, Transform, Load) operations with custom logic.
5. **GCP Workflows**: For orchestrating the data pipeline.

### **Data Sources**
- **Airport Data (Static)**: `airport_codes.csv`
  - Contains airport IDs, city, state, and airport names.
- **Flight Data (Dynamic)**: `flights.csv`
  - Contains carrier information, origin/destination airport IDs, and delays.

---

## **File Structure**

```
airline-data-ingestion-gcp/
├── data/
│   ├── airport_codes.csv          # Static airport data
│   ├── sample_flights.csv         # Initial sample flight data
│   └── new_flights.csv            # Example of new flight data
├── schemas/
│   ├── airport_schema.json        # BigQuery schema for airport data
│   ├── flight_schema.json         # BigQuery schema for flight data
├── workflows/
│   ├── workflow.yaml              # GCP Workflows YAML definition
├── scripts/
│   ├── create_resources.sh        # Script to create GCP resources
│   ├── delete_resources.sh        # Script to delete GCP resources
│   ├── dataflow_etl.py            # Custom Apache Beam script for ETL
├── .gitignore                     # Ignore unnecessary files
└── README.md                      # Documentation
```

---

## **Pipeline Flow**

1. **File Upload to GCS**:
   - Static (`airport_codes.csv`) and dynamic (`flights.csv`) data files are uploaded to GCS.

2. **GCS Notifications via Pub/Sub**:
   - Pub/Sub triggers the pipeline when a new file is uploaded.

3. **BigQuery Dataset Creation**:
   - Static airport data is stored in the `airport_dim` table.
   - A `flight_fact` table is created to store enriched data.

4. **ETL with Apache Beam**:
   - Flight data is enriched with airport data (city and state) based on Origin/Destination Airport IDs.

5. **Store Enriched Data in BigQuery**:
   - The processed data is written to the `flight_fact` table in BigQuery.

6. **Automation with GCP Workflows**:
   - Orchestrates the pipeline, from file upload to completion notification.

---

## **Step-by-Step Implementation**

### **1. Data Preparation**
- Place `airport_codes.csv` and `sample_flights.csv` in the `data/` folder.

### **2. Resource Creation**
Run the following script to create all necessary GCP resources:
```bash
bash scripts/create_resources.sh
```
This script will:
- Create a GCS bucket and upload data files.
- Create a Pub/Sub topic for GCS notifications.
- Create a BigQuery dataset and load the static airport data.

### **3. Dataflow ETL Job**
- The ETL process is handled by a custom Apache Beam script (`dataflow_etl.py`) that performs the following:
  1. Extracts `airport_codes.csv` (static airport metadata) and `flights.csv` (dynamic flight data) from GCS.
  2. Enriches flight data with city and state information for origin and destination airports.
  3. Writes the enriched data into the `flight_fact` table in BigQuery.

- To run the Dataflow job:
```bash
python scripts/dataflow_etl.py
```

### **4. Workflow Automation**
- Deploy the workflow YAML (`workflows/workflow.yaml`) to automate the pipeline:
```bash
gcloud workflows deploy airline-data-workflow --source=workflows/workflow.yaml --location=<REGION>
```
- Trigger the workflow:
```bash
gcloud workflows executions run airline-data-workflow
```

### **5. Testing the Pipeline**
- Simulate a file upload:
```bash
gsutil cp data/new_flights.csv gs://airline-data-ingestion/daily-flight-data/
```
- Monitor workflow execution:
```bash
gcloud workflows executions list --workflow=airline-data-workflow
```

### **6. Querying Data in BigQuery**
- Use the following query to validate the enriched data:
```sql
SELECT * FROM airline_data.flight_fact LIMIT 10;
```

### **7. Cleanup**
Run the cleanup script to delete all GCP resources:
```bash
bash scripts/delete_resources.sh
```

---

## **Sample Data**

### **Airport Data** (`airport_codes.csv`):
```csv
airport_id,city,state,name
10165,Adak Island,AK,Adak
10299,Anchorage,AK,Ted Stevens Anchorage International
10304,Aniak,AK,Aniak Airport
```

### **Flight Data** (`sample_flights.csv`):
```csv
Carrier,OriginAirportID,DestAirportID,DepDelay,ArrDelay
DL,11433,13303,-3,1
DL,14869,12478,0,-8
DL,14057,14869,-4,-15
```

---

## **Key GCP CLI Commands**

### **1. GCS Commands**
```bash
# Create GCS bucket
gsutil mb -p <PROJECT_ID> -l <REGION> gs://airline-data-ingestion/

# Upload files
gsutil cp data/airport_codes.csv gs://airline-data-ingestion/dimensional-data/
gsutil cp data/sample_flights.csv gs://airline-data-ingestion/daily-flight-data/
```

### **2. BigQuery Commands**
```bash
# Create dataset
bq mk --dataset <PROJECT_ID>:airline_data

# Load static data
bq load --source_format=CSV --skip_leading_rows=1 airline_data.airport_dim \
  gs://airline-data-ingestion/dimensional-data/airport_codes.csv schemas/airport_schema.json

# Create flight_fact table schema
bq mk --table <PROJECT_ID>:airline_data.flight_fact \
  Carrier:STRING,OriginAirportID:INTEGER,OriginCity:STRING,OriginState:STRING,DestAirportID:INTEGER,DestCity:STRING,DestState:STRING,DepDelay:INTEGER,ArrDelay:INTEGER
```

### **3. Workflow Deployment**
```bash
# Deploy workflow
gcloud workflows deploy airline-data-workflow --source=workflows/workflow.yaml --location=<REGION>
```

---

## **Future Enhancements**
1. Add monitoring using GCP Cloud Monitoring.
2. Implement additional error handling in the ETL pipeline.
3. Optimize BigQuery queries for better performance.

---
