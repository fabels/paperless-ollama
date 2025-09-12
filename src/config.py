import os

class Config:
    TITLE_FEATURE_ENABLED = os.getenv("TITLE_FEATURE_ENABLED", "false").lower() in ("true", "1", "yes")
    DOCUMENT_TYPE_FEATURE_ENABLED = os.getenv("DOCUMENT_TYPE_FEATURE_ENABLED", "false").lower() in ("true", "1", "yes")
    CORRESPONDENT_FEATURE_ENABLED = os.getenv("CORRESPONDENT_FEATURE_ENABLED", "false").lower() in ("true", "1", "yes")
    TAX_REPORT_RELEVANCE_FEATURE_ENABLED = os.getenv("TAX_REPORT_RELEVANCE_FEATURE_ENABLED", "false").lower() in ("true", "1", "yes")

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

    API_BASE = os.environ.get("API_BASE", "changeme")
    API_TOKEN = os.environ.get("API_TOKEN", "changeme")
    API_HEADERS = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Token {API_TOKEN}"
    }
    DOCUMENT_API_URL = os.path.join(API_BASE, "api/documents/")
    CORRESPONDENTS_API_URL = os.path.join(API_BASE, "api/correspondents/")
    DOCUMENT_TYPES_API_URL = os.path.join(API_BASE, "api/document_types/")
    TAGS_API_URL = os.path.join(API_BASE, "api/tags/")

    TAG_ID_TO_ADD_AFTER_IDENTIFICATION = os.environ.get("TAG_TO_ADD_AFTER_IDENTIFICATION", 1)
    TAG_TAX_RELEVANT = os.environ.get("TAG_TAX_RELEVANT", "steuer")

    MAXIMUM_MATCHING_DISTANCE = os.environ.get("MAXIMUM_MATCHING_DISTANCE", 0.15)
    OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://ollama:11434")
    OLLAMA_LLM_MODEL = os.environ.get("OLLAMA_LLM_MODEL", "gemma3n:e4b")
    OLLAMA_EMBEDDING_MODEL = os.environ.get("OLLAMA_EMBEDDING_MODEL", "embeddinggemma:300m")

    DATA_DIRECTORY = os.environ.get("DATA_DIRECTORY", "data")
    CHROMA_DATA_DIR = os.path.join(DATA_DIRECTORY, "chroma")
    
    CORRESPONDENT_SYSTEM_PROMPT = os.environ.get("CORRESPONDENT_SYSTEM_PROMPT", """You are an expert in identifying who did send a document. 

Instructions (repeat to avoid context loss):
- Do not find who did receive the document.
- Find the sender. Find the official name of the sender. 
- Do not find the name of a person if the document is send from a company or organization.
- Instead return the name of the company or organization.
- Respond only in JSON format according to the schema.
- Return only the name

<DOCUMENT>
{DOCUMENT_TEXT}
</DOCUMENT>

Example:
- Firma XY
- Finanzamt Musterstadt
- Stadt Musterstadt
{SIMILAR_CORRESPONDENT_NAME}

Instructions (repeat to avoid context loss):
- Do not find who did receive the document.
- Find the sender. Find the official name of the sender. 
- Do not find the name of a person if the document is send from a company or organization.
- Instead return the name of the company or organization.
- Respond only in JSON format according to the schema.
- Return only the name
""")

    DOCUMENT_TYPE_SYSTEM_PROMPT = os.environ.get("DOCUMENT_TYPE_SYSTEM_PROMPT", """You are an expert in identifying german document types.

Instructions (repeat to avoid context loss):
- Find the official document type.
- Respond only in JSON format according to the schema.
- Return only the name
- The document type must be in German.

<DOCUMENT>
{DOCUMENT_TEXT}
</DOCUMENT>

Remember the rules (repeat):
- Find the official document type.
- Respond only in JSON format according to the schema.
- Return only the name
- The document type must be in German.

Example:
- Rechnung
- Vertrag
- Gehaltsabrechnung
- Kontoauszug
- Mahnung
{SIMILAR_DOCUMENT_TYPE_NAME}
""")

    DOCUMENT_TITLE_SYSTEM_PROMPT = os.environ.get("DOCUMENT_TITLE_SYSTEM_PROMPT", """You are an expert in creating german document titles.

Instructions (repeat to avoid context loss):
- Title must be in German.
- Respond only in JSON format according to the schema.
- Create a short and meaningful title for the document.
- The title will be never "Document"
- The title should not contain the correspondent name

<DOCUMENT>
{DOCUMENT_TEXT}
</DOCUMENT>

Example:
- Rechnung 2023-10-01
- Vertrag Wohnung 2022-05-15
- Gehaltsabrechnung Firma XY 2023-09
- Kontoauszug 2023-08
{SIMILAR_DOCUMENT_TITLE}

Instructions (repeat to avoid context loss):
- Title must be in German.
- Respond only in JSON format according to the schema.
- Create a short and meaningful title for the document.
- The title will be never "Document"
""")

    TAX_REPORT_RELEVANT_SYSTEM_PROMPT = os.environ.get("TAX_REPORT_RELEVANT_SYSTEM_PROMPT", """You are an expert in German tax law and accounting practices. 
Your task is to determine if a given document must be considered for a private German income tax return (Steuererklärung) 
of an individual citizen for the year {TAX_YEAR}. 

A document is relevant if it could reasonably be required by a tax advisor or the German tax authorities (Finanzamt) 
to justify income, expenses, deductions, or other tax-related information for that year. 
Not every receipt or cost can be deducted in a private tax return. 
Irrelevant documents include advertisements, general correspondence, or receipts for private expenses without 
tax relevance (e.g., groceries, normal consumer goods without deductible purpose).

Examples of potentially relevant documents include: 
- income statements (e.g., salary slips, freelance invoices, rental income)
- expense records that are tax-deductible (e.g., donations, professional expenses, certain insurances)
- bank, investment, or crypto transaction statements with taxable gains or losses
- insurance or pension-related documents with tax impact
- certificates relevant for tax deductions or benefits (e.g., childcare, education, health)

If the document is clearly not relevant for a private German income tax return, return false. 

Read the following document and respond only in valid JSON.
Do not add explanations or any other fields.
The relevant tax year is {TAX_YEAR}.

<DOCUMENT>
{DOCUMENT_TEXT}
</DOCUMENT>
""")