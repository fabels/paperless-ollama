import logging
import chromadb

from config import Config

logger = logging.getLogger(__name__)

client = chromadb.PersistentClient(path=Config.CHROMA_DATA_DIR)

correspondents_collection = client.get_or_create_collection("correspondents")
document_types_collection = client.get_or_create_collection("document_types")
documents_collection = client.get_or_create_collection("documents")
tags_collection = client.get_or_create_collection("tags")