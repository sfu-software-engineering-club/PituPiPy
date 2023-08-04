from Crypto.PublicKey import RSA
from Crypto import Random


class MessageEncryption:
    def __init__(self):
        pass

    def read_key():
        h = open("mykey.pem", "r")
        key = RSA.importKey(h.read())
        h.close()
        return key

    def encrypt(private_key):
        priv_key = read_key()
        public_key = priv_key.publickey()
        encdata = public_key.encrypt(private_key, 32)

        return encdata

    def decrypt(public_key):
        priv_key = read_key()
        decdata = priv_key.decrypt(public_key)
        return decdata

    def generate_key():
        private_key = RSA.generate(1024)
        f = open("mykey.pem", "wb+")
        f.write(private_key.exportKey("PEM"))
        f.close()

    def generate_public_key(private_key):
        f = open("mykey.pem", "wb+")
        f.write(private_key.exportKey("PEM"))
        f.close()

    if __name__ == "__main__":
        msg = "python"

        ciphered = encrypt(smg.encode("utf-8"))
        print(ciphered)

        deciphered = decrypt(ciphered)
        print(deciphered)
