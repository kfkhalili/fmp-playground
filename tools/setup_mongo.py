# tools/setup_mongo.py

import logging
from dotenv import load_dotenv

# Import your helper from the package
from fmp_playground.utils import get_mongo_client

def main():
    logging.basicConfig(level=logging.INFO)

    # Load .env.local to get MONGODB_URI
    load_dotenv(".env.local")

    import os
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

    # Use your helper to connect
    client = get_mongo_client(mongo_uri)
    db = client["fmp"]
    collection = db["traded_list"]

    # Create a unique index on "symbol" if not already present
    collection.create_index([("symbol", 1)], name="symbol_unique_idx", unique=True)

    logging.info("Database 'fmp' and collection 'traded_list' created or verified.")
    logging.info("Unique index on 'symbol' created or verified.")
