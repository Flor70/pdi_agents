
import chromadb

client = chromadb.Client()
collection = client.get_collection(name="chroma_docs")
results = collection.get(ids=["page"])["documents"]
print(results) # Not found []
