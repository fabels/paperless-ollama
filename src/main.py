import flask
from flasgger import Swagger

from functions import identify_and_update_document
from functions import get_id_from_url
from logger import setup_logging
from paperless import get_document
from functions import sync_tags
from functions import sync_correspondents
from functions import sync_document_types

app = flask.Flask(__name__)
swagger = Swagger(app)

@app.route('/sync_tags', methods=['GET'])
def route_sync_tags():
    """Sync tags from Paperless
    ---
    get:
      description: Sync tags from Paperless
      responses:
        200:
          description: Tags synced successfully
          schema:
            type: object
            properties:
              status:
                type: string
                example: "success"
    """
    sync_tags()
    return {"status": "success"}

@app.route('/sync_correspondents', methods=['GET'])
def route_sync_correspondents():
    """Sync correspondents from Paperless
    ---
    get:
      description: Sync correspondents from Paperless
      responses:
        200:
          description: Correspondents synced successfully
          schema:
            type: object
            properties:
              status:
                type: string
                example: "success"
    """
    sync_correspondents()
    return {"status": "success"}

@app.route('/sync_document_types', methods=['GET'])
def route_sync_document_types():
    """Sync document types from Paperless
    ---
    get:
      description: Sync document types from Paperless
      responses:
        200:
          description: Document types synced successfully
          schema:
            type: object
            properties:
              status:
                type: string
                example: "success"
    """
    sync_document_types()
    return {"status": "success"}

@app.route('/identify', methods=['POST'])
def identify():
    """Identify document by URL
    ---
    post:
      description: Identify document by URL
      parameters:
        - in: body
          name: body
          schema:
            type: object
            properties:
              url:
                type: string
                example: "http://localhost/api/documents/1/"
      responses:
        200:
          description: Document identified successfully
          schema:
            type: object
            properties:
              status:
                type: string
                example: "success"
    """
    body = flask.request.get_json()
    url = body.get('url')
    id = get_id_from_url(url)
    document = get_document(id)

    identify_and_update_document(document)
    
    return {"status": "success"}

@app.route('/identify/<int:id>', methods=['POST'])
def identify_by_id(id):
    """Identify document by ID
    ---
    post:
      description: Identify document by ID
      parameters:
        - in: path
          name: id
          required: true
          type: integer
      responses:
        200:
          description: Document identified successfully
          schema:
            type: object
            properties:
              status:
                type: string
                example: "success"
    """
    document = get_document(id)

    identify_and_update_document(document)
    
    return {"status": "success"}


if __name__ == "__main__":
    setup_logging()

    app.run(host="0.0.0.0", port=5001)