import chromadb
import sys
import sqlite3

# Fix para versão do SQLite no Streamlit Cloud
if sqlite3.sqlite_version_info < (3, 35, 0):
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

client = chromadb.Client()
collection = client.get_collection(name="chroma_docs")
results = collection.get(ids=["page"])["documents"]
print(results) # Not found []