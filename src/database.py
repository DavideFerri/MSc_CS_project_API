from pymongo import MongoClient
from pymongo.database import Database
from src.config import Settings


# connect to cluster and create client of mock_database db (db_); within db_ "users" collection will be created
def get_dbs(verbose=False) -> Database:
    settings = Settings()
    db = MongoClient(settings.MONGO_DB_URL)[settings.MONGO_DB_ENV]
    try:
        print("Connected to MongoDB Atlas")
        if verbose:
            print(db.server_info())
    except Exception:
        print("Unable to connect MongoDB Atlas.")
    return db
