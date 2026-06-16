import os
import sys
from turtledemo import __main__

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

# If you are in a subfolder, this moves up ONE level to the root
root_dir = os.path.dirname(current_dir)

# Add root to path
sys.path.append(root_dir)


from dotenv import load_dotenv
load_dotenv()

CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_PORT = int(os.getenv("CHROMA_PORT"))

import chromadb

client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)

# List all collections
collections = client.list_collections()
print(f"Found {len(collections)} collections:")

for col in collections:
    print(f"\n📁 Collection Name: {col.name}")
    # Print the first 5 items inside the collection
    print(col.peek(limit=5))
#
# #Clear collection
# Retrieve the collection
#collection = client.get_collection(name="issue_db")
#
# Delete all items by passing all IDs inside it
#collection.delete(ids=collection.get()["ids"])