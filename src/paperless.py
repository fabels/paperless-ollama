import requests
import logging

from config import Config

logger = logging.getLogger(__name__)

def create_tag(name: str):
    logger.info(f"create_tag: {name}")
    data = {
        "name": name
    }
    response = requests.post(Config.TAGS_API_URL, headers=Config.API_HEADERS, json=data)
    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Fehler beim Erstellen des Tags: {response.status_code} - {response.text}")

def create_correspondent(name: str):
    logger.info(f"create_correspondent: {name}")
    data = {
        "name": name
    }
    response = requests.post(Config.CORRESPONDENTS_API_URL, headers=Config.API_HEADERS, json=data)
    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Fehler beim Erstellen des Korrespondenten: {response.status_code} - {response.text}")
    

def create_document_type(name: str):
    logger.info(f"create_document_type: {name}")
    data = {
        "name": name
    }
    response = requests.post(Config.DOCUMENT_TYPES_API_URL, headers=Config.API_HEADERS, json=data)
    if response.status_code == 201:
        response = response.json()
        return response
    else:
        raise Exception(f"Fehler beim Erstellen des Dokumententyps: {response.status_code} - {response.text}")
    
def update_document(
        document_id: int, 
        title: str = None, 
        correspondent_id: int = None, 
        document_type_id: int = None,
        document_tags: list = None
    ):
    logger.info(f"update_document: {document_id}")
    data = {}
    if title:
        data["title"] = title
    if correspondent_id:
        data["correspondent"] = correspondent_id
    if document_type_id:
        data["document_type"] = document_type_id
    if document_tags is not None:
        data["tags"] = document_tags

    logger.info(f"update_document data: {data}")

    response = requests.patch(f"{Config.API_BASE}/api/documents/{document_id}/", headers=Config.API_HEADERS, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Fehler beim Aktualisieren des Dokuments: {response.status_code} - {response.text}")
    
def get_correspondents():
    logger.info("get_correspondents")
    response = requests.get(Config.CORRESPONDENTS_API_URL, headers=Config.API_HEADERS)
    if response.status_code == 200:
        return response.json()['results']
    else:
        raise Exception(f"Fehler beim Abrufen der Korrespondenten: {response.status_code} - {response.text}")
    
def get_document_types():
    logger.info("get_document_types")
    response = requests.get(Config.DOCUMENT_TYPES_API_URL, headers=Config.API_HEADERS)
    if response.status_code == 200:
        return response.json()['results']
    else:
        raise Exception(f"Fehler beim Abrufen der Dokumententypen: {response.status_code} - {response.text}")

def get_document(id: str) -> dict:
    response = requests.get(f"{Config.DOCUMENT_API_URL}{id}/", headers=Config.API_HEADERS)
    if response.status_code == 200:
        return response.json()

    raise Exception(f"Fehler beim Abrufen des Dokuments: {response.status_code} - {response.text}")

def get_documents():
    response = requests.get(Config.DOCUMENT_API_URL, headers=Config.API_HEADERS)
    if response.status_code == 200:
        return response.json()['results']

    raise Exception(f"Fehler beim Abrufen der Dokumente: {response.status_code} - {response.text}")

def get_tags():
    response = requests.get(Config.TAGS_API_URL, headers=Config.API_HEADERS)
    if response.status_code == 200:
        return response.json()['results']

    raise Exception(f"Fehler beim Abrufen der Tags: {response.status_code} - {response.text}")