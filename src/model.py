from pydantic import BaseModel

""" Sender-Modell """
class Sender(BaseModel):
    """ Name of Sender """
    name: str

""" Document Type Model """
class DocumentType(BaseModel):
    """ Name of Document Type """
    name: str

""" Document Titel Model """
class DocumentTitel(BaseModel):
    """ Document Title """
    titel: str

""" Tax Report Relevant Model """
class TaxReportRelevant(BaseModel):
    """ Tax Report Relevance """
    relevant: bool