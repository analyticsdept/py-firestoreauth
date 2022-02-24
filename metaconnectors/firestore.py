from firebase_admin import credentials
from firebase_admin import firestore
from pathlib import Path
import firebase_admin
import os

class MetaFirestoreDocument():
    def __init__(self, id, data):
        self.id = id
        self.data = data
    
    def to_dict(self):
        return {"id": self.id, "data": self.data}

class MetaFirestore():
    def __init__(self, service_account_id, project_id = None):
        key_path = f"{str(Path(os.path.dirname(os.path.abspath(__file__))).parent)}/keys/{service_account_id}"
        if not firebase_admin._apps:
            cred = credentials.Certificate(key_path)
            _opts = {"projectId": project_id} if project_id else {}
            firebase_admin.initialize_app(cred, options=_opts)
        self.db = firestore.client()

    def read(self, collection, document=None):
        if collection and document:
            return self.read_document(collection, document)
        if collection and not document:
            return self.read_collection(collection)

    def read_collection(self, collection, document=None):
        try:
            db = firestore.client()
            docs = db.collection(collection).stream()
            # return [{"id": doc.id, "dict": doc.to_dict()} for doc in docs if doc.exists]
            return [MetaFirestoreDocument(doc.id, doc.to_dict()) for doc in docs if doc.exists]
        except Exception as e:
            raise Exception(f"could not read from collection {type(e).__name__} >> {str(e)}")

    def read_document(self, collection, document):
        try:
            db = firestore.client()
            doc_ref = db.collection(collection).document(document)
            doc = doc_ref.get()
            if doc.exists:
                # return {"id": doc.id, "dict": doc.to_dict()}
                return MetaFirestoreDocument(doc.id, doc.to_dict())
            else:
                raise Exception(f'document does not exist')
        except Exception as e:
            raise Exception(f"could not read document >> {type(e).__name__} >> {str(e)}")

    def write(self, collection, document, dictionary={}):
        try:
            db = firestore.client()
            doc_ref = db.collection(collection).document(document)
            doc_ref.set(dictionary)
        except Exception as e:
            raise Exception(f"could not write document >> {type(e).__name__} >> {str(e)}")
        else:
            return True

    def add(self, collection, dictionary={}):
        try:
            db = firestore.client()
            col_ref = db.collection(collection)
            col_ref.add(dictionary)
        except Exception as e:
            print(str(e))
            return False
        else:
            return True

    def update(self, collection, document, dictionary):
        try:
            db = firestore.client()
            ref = db.collection(collection).document(document)
            ref.update(dictionary)
        except Exception as e:
            print(str(e))
            return False
        else:
            return 
            
    def delete(self, collection, document):
        try:
            db = firestore.client()
            db.collection(collection).document(document).delete()
        except Exception as e:
            print(str(e))    
            return False
        else:
            return True