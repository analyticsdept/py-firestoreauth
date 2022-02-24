from constants import *
from metaconnectors import MetaFirestore
from metacrypto import MetaCrypto

class FirestoreAuth():
    """
    Firestore Auth context manager

    @Author: Rob / analyticsdept
    @Github: https://github.com/analyticsdept
    """

    def __init__(self, project=None, user=None, token=None) -> None:
        """
        Only passing in the project will create an unauthenticated instance
        """

        self.authenticated = False
        self.project = project
        self.user = user
        self.token = token
        self.should_authenticate = bool(bool(project) * bool(user) * bool(token))
        
    def __enter__(self):
        if self.should_authenticate:
            try: self.authenticate()
            except Exception as e: raise Exception(f'Error authenticating user: {str(e)}')  
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.authenticated = False

    def authenticate(self):
        try: user = self.encrypt_user()
        except Exception as e: raise Exception(str(e))

        try: stored_user = self.fetch_user().get(DATA, {}).get(self.project, None)
        except Exception as e: raise Exception(str(e))

        if user == stored_user:
            self.authenticated = True
        else:
            raise Exception('incorrect credentials')

    def fetch_user(self):
        client = MetaFirestore(FIRESTORE_DEFAULT_KEY)
        try: config = client.read_document(FIRESTORE_AUTH_COLLECTION, f'{self.user}')
        except Exception as e: raise Exception(f'could not connect to Firestore: {str(e)}')        
        
        if config == None:
            raise Exception(f'could not find project {self.project}')

        try: _dict = config.to_dict()
        except Exception as e: raise Exception(f'could not read project {self.project}: {str(e)}')
        else: return _dict

    def create_user(self, user, token):
        """Create new project on Firestore"""

        try: encrypted_token = self.encrypt_user(user, token)
        except Exception as e: raise Exception(f'could not encrypt user: {str(e)}')

        client = MetaFirestore(FIRESTORE_DEFAULT_KEY)

        try: existing_user_record = client.read_document(FIRESTORE_AUTH_COLLECTION, f'{user}').to_dict().get(DATA, {})
        except: existing_user_record = {}

        document = {**existing_user_record, **{self.project: encrypted_token}}

        try: client.write(FIRESTORE_AUTH_COLLECTION, f'{user}', document)
        except Exception as e: raise Exception(str(e))
        else: return True

    def encrypt_user(self, user=None, token=None):
        _user = user if user else self.user
        _token = token if token else self.token
        user_obj = {AUTH_KEY_USER: _user, AUTH_KEY_TOKEN: _token, AUTH_KEY_PROJECT: self.project}
        
        try:
            m = MetaCrypto()
            _encrypted = m.encrypt_symmetric_siv(user_obj, True)
        except Exception as e: raise Exception(str(e))
        else: return _encrypted