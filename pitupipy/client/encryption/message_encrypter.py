from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import ast

class Key:
    def __init__(self):
        self.priv_key = None
        self.pub_key = None

    def generate_keys(self): #generate a unique private/public keys set one time
        self.priv_key = RSA.generate(1024)
        self.pub_key = self.priv_key.publickey()

    def encrypt(self, msg): #encrypt message with the key
        encryptor = PKCS1_OAEP.new(self.pub_key)
        encrypted = encryptor.encrypt(msg)
        return encrypted
  
    def decrypt(self, msg): #decrypt message with the key
        decryptor = PKCS1_OAEP.new(self.priv_key)
        decrypted = decryptor.decrypt(ast.literal_eval(str(msg)))
        return decrypted 
