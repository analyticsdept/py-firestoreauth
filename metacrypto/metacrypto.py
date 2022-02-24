from ast import literal_eval
from base64 import b64decode, b64encode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from random import choices
from pathlib import Path
from string import ascii_letters, digits
import json
import os

def get_base_path():
    base = str(Path(os.path.dirname(os.path.abspath(__file__))).parent) if str(Path(os.path.dirname(os.path.abspath(__file__))).parent) != "/" else ""
    if len(base) > 0 and base[-1] == "/":
        base = base[len(base)-1]
    base = "" if base == "/" else base
    return f"{base}"

class MetaCrypto():
    def __init__(self):
        pass

    def decoder(self, data):
        if data == None:
            raise Exception('no data to decode')

        if isinstance(data, bytes):
            return b64decode(data).decode('utf-8')
        elif isinstance(data, dict) or isinstance(data, list):
            return data
        else:
            return b64decode(data.encode('utf-8')).decode('utf-8')

    def encoder(self, data):
        if data == None:
            raise Exception('no data to encode')

        if isinstance(data, bytes):
            return b64encode(data)
        else:
            return b64encode(json.dumps(data).encode('utf-8'))

    def base64_encoder(self, message):
        if type(message) in [dict, list]:
            message = json.dumps(message)

        return b64encode(message.encode('utf-8')).decode('utf-8')
        
    def base64_decoder(self, message):
        return b64decode(json.dumps(message).encode('utf-8')).decode('utf-8')

    def encode_data(self, data):
        if type(data) in [dict, list]:
            data = json.dumps(data)
        return data.encode('utf-8')

    def decode_data(self, data):
        return b64decode(data).decode('utf-8')

    def generate_bytes(self, _length=16):
        return get_random_bytes(_length)

    def generate_siv_key(self, header=None):
        if header == None:
            header = ''.join(choices(ascii_letters + digits, k=24))
        
        _key = str(b64encode(get_random_bytes(32)))
        _nonce = str(b64encode(get_random_bytes(16)))

        return {
            'header': header.replace(' ', '-').replace('\n', '_'),
            'key': _key,
            'nonce': _nonce
        }

    def unpack_siv_key(self, key):

        _header, _key, _nonce = None, None, None

        if isinstance(key, str):
            try: key = b64decode(key)
            except: pass

            try: key = json.loads(key, strict=False)
            except: raise Exception('could not unpack sivkey')
        
        if {'nonce', 'header', 'ciphertext', 'tag'} <= key.keys():
            key = self.decrypt_symmetric_siv(key, True)
            key = json.loads(key.decode('utf-8')) if isinstance(key, bytes) else json.loads(key)

        if 'header' in key.keys():
            _header = key['header'].encode('utf-8')
        if 'key' in key.keys():
            _key = b64decode(literal_eval(key['key']))
        if 'nonce' in key.keys():
            _nonce = b64decode(literal_eval(key['nonce']))

        return _header, _key, _nonce      

    def encrypt_symmetric_siv(self, data=None, use_default_key=False, sivkey=None):

        if not data:
            return data

        _sivkey = json.loads(open(f'{get_base_path()}/keys/siv__secret__.json').read()) if use_default_key else sivkey
        header, key, nonce = self.unpack_siv_key(_sivkey)
        
        data = self.encoder(data)
        
        cipher = AES.new(key, AES.MODE_SIV, nonce=nonce)    # static nonce == deterministic encryption
        cipher.update(header)
        ciphertext, tag = cipher.encrypt_and_digest(data)

        json_k = [ 'nonce', 'header', 'ciphertext', 'tag' ]
        json_v = [ b64encode(x).decode('utf-8') for x in (nonce, header, ciphertext, tag) ]
        result = json.dumps(dict(zip(json_k, json_v)))

        return b64encode(result.encode('utf-8')).decode('utf-8')

    def decrypt_symmetric_siv(self, data=None, use_default_key=False, sivkey=None) -> dict:

        _sivkey = json.loads(open(f'{get_base_path()}/keys/siv__secret__.json').read()) if use_default_key else sivkey
        header, key, nonce = self.unpack_siv_key(_sivkey)

        try:
            b64 = data if isinstance(data, dict) or isinstance(data, list) else json.loads(self.decoder(data))
            json_k = [ 'nonce', 'header', 'ciphertext', 'tag' ]
            jv = {k:b64decode(b64[k]) for k in json_k}

            cipher = AES.new(key, AES.MODE_SIV, nonce=jv['nonce'])
            cipher.update(jv['header'])
            plaintext = cipher.decrypt_and_verify(jv['ciphertext'], jv['tag'])
        except (ValueError, KeyError) as e:
            raise Exception(f'could not decrypt data: {type(e).__name__} >> {str(e)}')
        else:
            return b64decode(plaintext).decode('utf-8')