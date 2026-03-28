#!/usr/bin/env python

import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm


DTYPE = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

PARSE_DATES = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]


def run():

    # PostgreSQL connection settings
    pg_user = "root"
    pg_pass = "root"
    pg_host = "localhost"
    pg_port = 5432
    pg_db = "ny_taxi"

    # Dataset settings
    year = 2021
    month = 1
    chunksize = 100000
    target_table = "yellow_taxi_data"

    prefix = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow"
    url = f"{prefix}/yellow_tripdata_{year}-{month:02d}.csv.gz"

    # Database engine
    engine = create_engine(
        f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
    )

    # Read CSV in chunks
    df_iter = pd.read_csv(
        url,
        dtype=DTYPE,
        parse_dates=PARSE_DATES,
        iterator=True,
        chunksize=chunksize
    )

    first = True

    for df_chunk in tqdm(df_iter):

        if first:
            # Create table schema
            df_chunk.head(0).to_sql(
                name=target_table,
                con=engine,
                if_exists="replace",
                index=False
            )
            first = False

        # Insert data
        df_chunk.to_sql(
            name=target_table,
            con=engine,
            if_exists="append",
            index=False,
            method="multi"
        )


if __name__ == "__main__":
    run()