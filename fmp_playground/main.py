# fmp_playground/main.py
import os
import fmpsdk
import pandas as pd
import logging

from fmp_playground.logging_config import setup_logging
from fmp_playground.utils import get_mongo_client
from pymongo import UpdateOne
from dotenv import load_dotenv


def main():
    setup_logging()

    load_dotenv(".env.local")

    fmp_api_key = os.getenv("FMP_API_KEY")

    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

    # Fetch and filter data
    df_available = pd.DataFrame(fmpsdk.available_traded_list(apikey=fmp_api_key))
    df_xetra = df_available.drop(columns=["price"])
    records = df_xetra.to_dict("records")

    # Create a function that maps a record to an UpdateOne operation
    def record_to_upsert(doc):
        return UpdateOne(
            {"symbol": doc["symbol"]},  # query
            {"$set": doc},             # update
            upsert=True
        )

    # Build the list of upsert operations
    operations = list(map(record_to_upsert, records))

    # Execute the bulk upsert
    try:
        client = get_mongo_client(mongo_uri)
        result = client.fmp.traded_list.bulk_write(operations, ordered=False)
        logging.info(
            f"Matched: {result.matched_count}, "
            f"Modified: {result.modified_count}, "
            f"Upserted: {result.upserted_count}"
        )
    except Exception as e:
        logging.error("Bulk upsert error:", e)