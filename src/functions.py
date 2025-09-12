import re
import logging

from datetime import datetime

from llm import generate
from llm import embed
from config import Config
from model import DocumentTitel
from model import TaxReportRelevant
from model import DocumentType
from model import Sender
from paperless import create_correspondent
from paperless import get_tags
from paperless import create_document_type
from paperless import get_correspondents
from paperless import get_document_types
from paperless import update_document
from paperless import get_documents
from paperless import create_tag
from chroma import correspondents_collection
from chroma import document_types_collection
from chroma import documents_collection
from chroma import tags_collection

logger = logging.getLogger(__name__)

def delete_stale_tags(tags):
    existing_ids = [str(t["id"]) for t in tags]
    all_ids = tags_collection.get()['ids']
    ids_to_delete = [id for id in all_ids if id not in existing_ids]
    if ids_to_delete:
        logger.info(f"Deleting {len(ids_to_delete)} tags that are not in Paperless anymore.")
        tags_collection.delete(ids=ids_to_delete)

def sync_tags():
    logger.info("Synchronizing tags...")
    tags = get_tags()
    delete_stale_tags(tags)
    for tag in tags:
        tag_existing = tags_collection.get(ids=[str(tag["id"])])
        saved_tag_has_same_name = (tag_existing['metadatas'] and tag_existing['metadatas'][0]['name'] == tag['name'])
        if tag_existing['ids'] and saved_tag_has_same_name:
            logger.info(f"Tag with ID {tag['id']} and name '{tag['name']}' already exists in ChromaDB. Skipping upsert.")
            continue
        logger.info(f"Processing tag: {tag['name']}")
        embedding_response = embed(model=Config.OLLAMA_EMBEDDING_MODEL, input=tag["name"])
        embeddings = embedding_response["embeddings"]
        tags_collection.upsert(
            documents=[tag["name"]],
            ids=[str(tag["id"])],
            metadatas=[{"id": str(tag["id"]), "name": tag["name"]}],
            embeddings=embeddings
        )

def create_tag_if_not_exists(name: str):
    exiting_tags = tags_collection.get()
    for existing_tag in exiting_tags['metadatas']:
        if existing_tag['name'].lower() == name.lower():
            logger.info(f"Tag '{name}' already exists with ID {existing_tag['id']}.")
            return existing_tag

    logger.info(f"Tag '{name}' does not exist. Creating a new tag.")
    new_tag = create_tag(name)
    embedding_response = embed(model=Config.OLLAMA_EMBEDDING_MODEL, input=new_tag["name"])
    embeddings = embedding_response["embeddings"]
    tags_collection.upsert(
        documents=[new_tag["name"]],
        ids=[str(new_tag["id"])],
        metadatas=[{"id": str(new_tag["id"]), "name": new_tag["name"]}],
        embeddings=embeddings
    )
    return new_tag

def get_correspondent_by_id(correspondent_id: int):
    correspondent = correspondents_collection.get(ids=[str(correspondent_id)])
    if correspondent['ids']:
        return correspondent['metadatas'][0]
    return None

def sync_correspondents():
    logger.info("Synchronizing correspondents...")
    correspondents = get_correspondents()
    delete_stale_correspondents(correspondents)
    for correspondent in correspondents:
        correspondent_existing = correspondents_collection.get(ids=[str(correspondent["id"])])
        saved_correspondent_has_same_name = (correspondent_existing['metadatas'] and correspondent_existing['metadatas'][0]['name'] == correspondent['name'])
        if correspondent_existing['ids'] and saved_correspondent_has_same_name:
            logger.info(f"Correspondent with ID {correspondent['id']} and name '{correspondent['name']}' already exists in ChromaDB. Skipping upsert.")
            continue
        logger.info(f"Processing correspondent: {correspondent['name']}")
        embedding_response = embed(model=Config.OLLAMA_EMBEDDING_MODEL, input=correspondent["name"])
        embeddings = embedding_response["embeddings"]
        correspondents_collection.upsert(
            documents=[correspondent["name"]],
            ids=[str(correspondent["id"])],
            metadatas=[{"id": str(correspondent["id"]), "name": correspondent["name"]}],
            embeddings=embeddings
        )

def delete_stale_correspondents(correspondents):
    existing_ids = [str(c["id"]) for c in correspondents]
    all_ids = correspondents_collection.get()['ids']
    ids_to_delete = [id for id in all_ids if id not in existing_ids]
    if ids_to_delete:
        logger.info(f"Deleting {len(ids_to_delete)} correspondents that are not in Paperless anymore.")
        correspondents_collection.delete(ids=ids_to_delete)

def get_document_type_by_id(document_type_id: int):
    document_type = document_types_collection.get(ids=[str(document_type_id)])
    if document_type['ids']:
        return document_type['metadatas'][0]
    return None

def sync_document_types():
    logger.info("Synchronizing document types...")
    document_types = get_document_types()
    delete_stale_document_types(document_types)
    for document_type in document_types:
        document_type_existing = document_types_collection.get(ids=[str(document_type["id"])])
        saved_document_type_has_same_name = (document_type_existing['metadatas'] and document_type_existing['metadatas'][0]['name'] == document_type['name'])
        if document_type_existing['ids'] and saved_document_type_has_same_name:
            logger.info(f"Document type with ID {document_type['id']} and name '{document_type['name']}' already exists in ChromaDB. Skipping upsert.")
            continue
        logger.info(f"Processing document type: {document_type['name']}")
        embedding_response = embed(model=Config.OLLAMA_EMBEDDING_MODEL, input=document_type["name"])
        embeddings = embedding_response["embeddings"]
        document_types_collection.upsert(
            documents=[document_type["name"]],
            ids=[str(document_type["id"])],
            metadatas=[{"id": str(document_type["id"]), "name": document_type["name"]}],
            embeddings=embeddings
        )

def delete_stale_document_types(document_types):
    existing_ids = [str(dt["id"]) for dt in document_types]
    all_ids = document_types_collection.get()['ids']
    ids_to_delete = [id for id in all_ids if id not in existing_ids]
    if ids_to_delete:
        logger.info(f"Deleting {len(ids_to_delete)} document types that are not in Paperless anymore.")
        document_types_collection.delete(ids=ids_to_delete)

def sync_documents(pre_generated_embedding = None):
    logger.info("Synchronizing documents...")
    documents = get_documents()
    delete_stale_documents(documents)
    for document in documents:
        document_existing = documents_collection.get(ids=[str(document["id"])])
        if document_existing['ids']:
            logger.info(f"Document with ID {document['id']} already exists in ChromaDB. Skipping upsert.")
            continue

        logger.info(f"Processing document: {document['id']} - {document['title']}")
        if pre_generated_embedding:
            embeddings = pre_generated_embedding
        else:
            embedding_response = embed(model=Config.OLLAMA_EMBEDDING_MODEL, input=document["content"])
            embeddings = embedding_response["embeddings"]
        documents_collection.upsert(
            documents=[document["content"]],
            ids=[str(document["id"])],
            metadatas=[{
                "id": str(document["id"]), 
                "title": document["title"],
                "document_type_id": str(document["document_type"]),
                "correspondent_id": str(document["correspondent"])
                }],
            embeddings=embeddings
        )

def delete_stale_documents(documents):
    existing_ids = [str(doc["id"]) for doc in documents]
    all_ids = documents_collection.get()['ids']
    ids_to_delete = [id for id in all_ids if id not in existing_ids]
    if ids_to_delete:
        logger.info(f"Deleting {len(ids_to_delete)} documents that are not in Paperless anymore.")
        documents_collection.delete(ids=ids_to_delete)

def search_similar_documents(content: str):
    embedding_response = embed(model=Config.OLLAMA_EMBEDDING_MODEL, input=content)
    embeddings = embedding_response["embeddings"]
    matching_documents = documents_collection.query(
        query_embeddings=embeddings,
        n_results=1
    )
    matching_documents_with_distances = sorted([
        (match, distance)
        for match, distance in zip(matching_documents['metadatas'][0], matching_documents['distances'][0])
        if distance <= Config.MAXIMUM_MATCHING_DISTANCE
    ], key=lambda x: x[1])

    if len(matching_documents_with_distances) == 0:
        logger.info("No similar documents found.")
        return (None, embeddings)

    return (matching_documents_with_distances[0], embeddings)

def get_head_and_tail(text: str, head_length: int = 1000, tail_length: int = 500) -> str:
    if len(text) <= head_length + tail_length:
        return text
    head = text[:head_length]
    tail = text[-tail_length:]

    template = """<HEAD>
{head}
</HEAD>
<TAIL>
{tail}
</TAIL>"""

    return template.format(head=head, tail=tail)

def generate_title(content: str, similar_document_title: str) -> str:

    document_title_system_prompt_formatted = Config.DOCUMENT_TITLE_SYSTEM_PROMPT.format(
        DOCUMENT_TEXT=content, SIMILAR_DOCUMENT_TITLE=similar_document_title
    )

    document_title_response = generate(
        prompt=document_title_system_prompt_formatted,
        model=Config.OLLAMA_LLM_MODEL,
        format=DocumentTitel.model_json_schema()
    )

    try:
        document_title_information = DocumentTitel.model_validate_json(
            document_title_response.response
        )
        logger.info(f"Generated title: {document_title_information.titel}")
        return document_title_information.titel
    except Exception as e:
        raise Exception("Fehler bei der Validierung des Dokumenttitels") from e

def generate_correspondent(content: str, similar_correspondent_name: str) -> str:
    correspondent_system_prompt_formatted = Config.CORRESPONDENT_SYSTEM_PROMPT.format(
        DOCUMENT_TEXT=content,
        SIMILAR_CORRESPONDENT_NAME=similar_correspondent_name
    )

    correspondent_response = generate(
        prompt=correspondent_system_prompt_formatted,
        model=Config.OLLAMA_LLM_MODEL,
        format=Sender.model_json_schema()
    )

    try:
        sender_information = Sender.model_validate_json(
            correspondent_response.response
        )
        logger.info(f"Identified sender: {sender_information.name}")
    except Exception as e:
        raise Exception("Fehler bei der Validierung des Senders") from e

    embedding_response = embed(model=Config.OLLAMA_EMBEDDING_MODEL, input=sender_information.name)
    embeddings = embedding_response["embeddings"]
    matching_correspondents = correspondents_collection.query(
        query_embeddings=embeddings,
        n_results=2
    )
    logger.info(f"Matching correspondents: {matching_correspondents}")
    matching_correspondents = sorted([
        (match, distance) for match, distance in zip(matching_correspondents['metadatas'][0], matching_correspondents['distances'][0])
        if distance <= Config.MAXIMUM_MATCHING_DISTANCE
    ], key=lambda x: x[1])

    if len(matching_correspondents) == 0:
        logger.info(f"No matching correspondent found for '{sender_information.name}', creating new correspondent.")
        correspondent = create_correspondent(name=sender_information.name)
        sync_correspondents()
        return correspondent

    logger.info(f"Found matching correspondent: {matching_correspondents[0][0]['name']} with distance {matching_correspondents[0][1]}")
    return matching_correspondents.pop(0)[0]

def generate_document_type(content: str, similar_document_type_name: str) -> str:
    document_type_system_prompt_formatted = Config.DOCUMENT_TYPE_SYSTEM_PROMPT.format(
        DOCUMENT_TEXT=content,
        SIMILAR_DOCUMENT_TYPE_NAME=similar_document_type_name
    )

    document_type_response = generate(
        prompt=document_type_system_prompt_formatted,
        model=Config.OLLAMA_LLM_MODEL,
        format=DocumentType.model_json_schema()
    )

    try:
        document_type_information = DocumentType.model_validate_json(
            document_type_response.response
        )
        logger.info(f"Identified document type: {document_type_information.name}")
    except Exception as e:
        raise Exception("Fehler bei der Validierung des Dokumenttyps") from e

    embedding_response = embed(model=Config.OLLAMA_EMBEDDING_MODEL, input=document_type_information.name)
    embeddings = embedding_response["embeddings"]
    matching_document_types = document_types_collection.query(
        query_embeddings=embeddings,
        n_results=2
    )

    logger.info(f"Matching document types: {matching_document_types}")

    matching_document_types_with_distances = sorted([
        (match, distance)
        for match, distance in zip(matching_document_types['metadatas'][0], matching_document_types['distances'][0])
        if distance <= Config.MAXIMUM_MATCHING_DISTANCE
    ], key=lambda x: x[1])

    if len(matching_document_types_with_distances) == 0:
        logger.info(f"No matching document type found for '{document_type_information.name}', creating new document type.")
        document_type = create_document_type(name=document_type_information.name)
        sync_document_types()
        return document_type

    logger.info(f"Found matching document type: {matching_document_types_with_distances[0][0]['name']} with distance {matching_document_types_with_distances[0][1]}")
    return matching_document_types_with_distances.pop(0)[0]

def generate_tax_report_relevance(content: str) -> bool:
    next_year = datetime.now().year + 1
    tax_report_relevance_system_prompt_formatted = Config.TAX_REPORT_RELEVANT_SYSTEM_PROMPT.format(
        DOCUMENT_TEXT=content, TAX_YEAR=next_year
    )

    tax_report_relevance_response = generate(
        prompt=tax_report_relevance_system_prompt_formatted,
        model=Config.OLLAMA_LLM_MODEL,
        format=TaxReportRelevant.model_json_schema()
    )

    try:
        tax_report_relevance_information = TaxReportRelevant.model_validate_json(
            tax_report_relevance_response.response
        )
        logger.info(f"Generated tax report relevance: {tax_report_relevance_information.relevant}")
        return tax_report_relevance_information.relevant
    except Exception as e:
        raise Exception("Fehler bei der Validierung der Steuerberichtsrelevanz") from e

def get_id_from_url(url: str) -> int:
    logger.info(f"Extracting ID from URL: {url}")
    m = re.search(r'/documents/(\d+)/?$', url.strip())
    if m:
        return int(m.group(1))
    
    raise ValueError("Invalid URL format")

def identify_and_update_document(document):

    sync_correspondents()
    sync_document_types()
    sync_tags()
    delete_stale_documents(get_documents())

    content = document["content"]

    similar_title = ''
    similar_correspondent = ''
    similar_document_type = ''
    (similar_document, embeddings) = search_similar_documents(content)
    if similar_document:
        logger.info(f"Found similar document with title: {similar_document[0]['title']} and distance {similar_document[1]}")
        similar_correspondent = get_correspondent_by_id(similar_document[0]['correspondent_id'])
        similar_document_type = get_document_type_by_id(similar_document[0]['document_type_id'])
        similar_title = similar_document[0]['title']
        similar_correspondent = similar_correspondent['name'] if similar_correspondent else ''
        similar_document_type = similar_document_type['name'] if similar_document_type else ''


    head_and_tail = get_head_and_tail(content)
    title = None
    correspondent = None
    document_type = None
    tax_report_relevance = False
    if Config.TITLE_FEATURE_ENABLED:
        title = generate_title(head_and_tail, similar_document_title=similar_title)
    if Config.CORRESPONDENT_FEATURE_ENABLED:
        correspondent = generate_correspondent(head_and_tail, similar_correspondent_name=similar_correspondent)['id']
    if Config.DOCUMENT_TYPE_FEATURE_ENABLED:
        document_type = generate_document_type(head_and_tail, similar_document_type_name=similar_document_type)['id']
    if Config.TAX_REPORT_RELEVANCE_FEATURE_ENABLED:
        tax_report_relevance = generate_tax_report_relevance(content)

    document_tags = document.get("tags", [])
    if tax_report_relevance:
        logger.info("Document is tax report relevant.")
        next_year = datetime.now().year + 1
        tax_tag = Config.TAG_TAX_RELEVANT + " " + str(next_year)
        tag = create_tag_if_not_exists(tax_tag)
        if tag['id'] not in document_tags:
            document_tags.append(tag['id'])
            logger.info(f"Added tax report tag '{tax_tag}' to document.")

    # Always add the identification tag
    identification_tag_is_set = Config.TAG_ID_TO_ADD_AFTER_IDENTIFICATION is not None 
    identification_tag_is_present = Config.TAG_ID_TO_ADD_AFTER_IDENTIFICATION in document_tags
    if identification_tag_is_set and not identification_tag_is_present:
        logger.info(f"Adding identification tag with ID {Config.TAG_ID_TO_ADD_AFTER_IDENTIFICATION} to document.")
        document_tags.append(Config.TAG_ID_TO_ADD_AFTER_IDENTIFICATION)

    updated_document = update_document(
        document_id=document["id"],
        title=title,
        correspondent_id=correspondent,
        document_type_id=document_type,
        document_tags=document_tags
    )

    sync_documents(pre_generated_embedding=embeddings)
    
    return updated_document