import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings(persist_directory="./unkakunni"))
collection = client.get_collection("techno_ai")

print("COUNT:", collection.count())