import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import csv

# Function to parse airport data
def parse_airport(row):
    fields = list(csv.reader([row]))[0]
    return int(fields[0]), {"city": fields[1], "state": fields[2]}

# Function to parse flight data
def parse_flight(row):
    fields = list(csv.reader([row]))[0]
    return {
        "Carrier": fields[0],
        "OriginAirportID": int(fields[1]),
        "DestAirportID": int(fields[2]),
        "DepDelay": int(fields[3]),
        "ArrDelay": int(fields[4])
    }

# Function to enrich flight data with airport metadata
def enrich_flight_data(flight, airport_dict):
    origin = airport_dict.get(flight["OriginAirportID"], {})
    dest = airport_dict.get(flight["DestAirportID"], {})
    return {
        "Carrier": flight["Carrier"],
        "OriginAirportID": flight["OriginAirportID"],
        "OriginCity": origin.get("city", ""),
        "OriginState": origin.get("state", ""),
        "DestAirportID": flight["DestAirportID"],
        "DestCity": dest.get("city", ""),
        "DestState": dest.get("state", ""),
        "DepDelay": flight["DepDelay"],
        "ArrDelay": flight["ArrDelay"]
    }

# Main pipeline function
def run():
    # Define pipeline options
    options = PipelineOptions(
        runner='DataflowRunner',
        project='<PROJECT_ID>',
        region='<REGION>',
        temp_location='gs://airline-data-ingestion/temp/',
        staging_location='gs://airline-data-ingestion/staging/'
    )

    with beam.Pipeline(options=options) as p:
        # Read airport data
        airport_data = (
            p
            | 'Read Airport Data' >> beam.io.ReadFromText('gs://airline-data-ingestion/dimensional-data/airport_codes.csv')
            | 'Parse Airport Data' >> beam.Map(parse_airport)
            | 'To Dictionary' >> beam.transforms.util.AsDict()
        )

        # Read flight data
        flight_data = (
            p
            | 'Read Flight Data' >> beam.io.ReadFromText('gs://airline-data-ingestion/daily-flight-data/sample_flights.csv')
            | 'Parse Flight Data' >> beam.Map(parse_flight)
        )

        # Enrich flight data
        enriched_data = (
            flight_data
            | 'Enrich Flight Data' >> beam.Map(enrich_flight_data, airport_dict=beam.pvalue.AsDict(airport_data))
        )

        # Write enriched data to BigQuery
        enriched_data | 'Write to BigQuery' >> beam.io.WriteToBigQuery(
            '<PROJECT_ID>:airline_data.flight_fact',
            schema=(
                'Carrier:STRING,OriginAirportID:INTEGER,OriginCity:STRING,OriginState:STRING,'
                'DestAirportID:INTEGER,DestCity:STRING,DestState:STRING,DepDelay:INTEGER,ArrDelay:INTEGER'
            ),
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
        )

if __name__ == '__main__':
    run()
