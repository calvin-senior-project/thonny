import pyDH
import threading
import os
from cryptography.fernet import Fernet
from binascii import unhexlify, b2a_base64

GROUP = 16
class Crypt:
    def __init__(self, pwd):
        self._dh = pyDH.DiffieHellman(GROUP)
        
        self._pwd_key = Fernet.generate_key()
        self._sess_key = Fernet.generate_key()
        self._sess_crypt = Fernet(self._sess_key)

        self._pwd_hash = Fernet(self._pwd_key).encrypt(bytes(pwd, "utf-8"))

        
        self._dh_lock = threading.Lock()
        self._pwd_lock = threading.Lock()

    def gen_handshake_pub(self):
        with self._dh_lock:
            return self._dh.gen_public_key()

    def get_handshake_shared(self, other_pub):
        with self._dh_lock:
            return self._dh.gen_shared_key(other_pub)

    def get_handshake_pwd_key(self, other_pub):
        key = b2a_base64(unhexlify(self._dh.gen_shared_key(other_pub)))
        with self._pwd_lock:
            return Fernet(key).encrypt(self._pwd_key)

    def get_session_key(self):
        return self._sess_key

    def auth(self, _hash):
        '''
        Checks if the _hash matches the password hash stored in memory.
        If it does, the function updates the pwd key and hash and returns true, Returns False otherwise.
        '''
        ret = self._pwd_hash == _hash
        self._update_pwd_key()
        return ret
    
    def encrypt(self, plaintext, key = None):
        if key != None:
            return Fernet(key).encrypt(plaintext)
        
        return self._sess_crypt.encrypt(plaintext)
    
    def decrypt(self, ciphertext, key = None):
        if key != None:
            return Fernet(key).decrypt(ciphertext)
        else:
            return self._sess_crypt.decrypt(ciphertext)
    
    def _update_pwd_key(self):
        with self._pwd_lock:
            pwd = Fernet(self._pwd_key).decrypt(self._pwd_hash)
            self._pwd_key = Fernet.generate_key()
            self._pwd_hash = Fernet(self._pwd_key).encrypt(pwd)
    
    def _replace_handshake_key(self):
        with self._dh_lock:
            self._dh = pyDH.DiffieHellman(GROUP)

if __name__ == "__main__":
    class CryptTester:
        def consturctor(self):
            print("- Testing constructor... ", end = "")

            try:
                c = Crypt()
            except (TypeError):
                print("0...", end = "\t")
            
            c = Crypt("test_pass")

            assert(isinstance(c._dh, pyDH.DiffieHellman))
            assert(isinstance(c._sess_crypt, Fernet))
            assert(bytes("test_pass", "utf-8") == Fernet(c._pwd_key).decrypt(c._pwd_hash))
            print(" 1...\tPassed")

        def get_handshake_pub(self):
            print("- Testing get_handshake_pub... ", end = "")
            c = Crypt("")
            assert(c._dh.gen_public_key() == c.gen_handshake_pub())
            print("Passed")

        def get_handshake_shared(self):
            print("- Testing get_handshake_shared... ", end = "")
            c = Crypt("")
            dh = pyDH.DiffieHellman(GROUP)
            c_pub = c.gen_handshake_pub()
            assert(c.get_handshake_shared(dh.gen_public_key()) == dh.gen_shared_key(c.gen_handshake_pub()))
            print("Passed")

        def get_pwd_key(self):
            print("- Testing get_pwd_key... ", end = "")
            c = Crypt("test_password")
            dh = pyDH.DiffieHellman(GROUP)
            
            dh_pub = dh.gen_public_key()
            c_pub = c.gen_handshake_pub()
            priv_key = b2a_base64(unhexlify(dh.gen_shared_key(c_pub)))
            
            assert(priv_key == b2a_base64(unhexlify(c.get_handshake_shared(dh_pub))))
            assert(c._pwd_key == Fernet(priv_key).decrypt(c.get_handshake_pwd_key(dh_pub)))
            print("Passed")

        def get_session_key(self):
            print("- Testing get_session_key... ", end = "")
            c = Crypt("test_password")
            assert(c.get_session_key() == c._sess_key)
            print("Passed")
        
        def auth(self):
            print("- Testing auth... ", end = "")
            c = Crypt("test_password")
            c_hash = c._pwd_hash
            c_key = c._pwd_key

            assert(c.auth(c_hash))
            assert(c._pwd_hash != c_hash)
            assert(c._pwd_key != c_key)
            print("Passed")
        
        def encrypt(self):
            print("- Testing encrypt... ")
            c = Crypt("test_password")

            print("\t > Without key... ", end = "")
            text = bytes("Test message", "utf-8")
            assert(Fernet(c._sess_key).decrypt(c.encrypt(text)) == text)
            print("Passed")

            print("\t > With key... ", end = "")
            key = Fernet.generate_key()
            assert(Fernet(key).decrypt(c.encrypt(text, key)) == text)
            print("Passed")

            print("\t Passed")
        
        def decrypt(self):
            print("- Testing decrypt... ")
            c = Crypt("test_password")

            print("\t > Without key... ", end = "")
            text = bytes("Test message", "utf-8")
            assert(c.decrypt(Fernet(c._sess_key).encrypt(text)) == text)
            print("Passed")

            print("\t > With key... ", end = "")
            key = Fernet.generate_key()
            assert(c.decrypt(Fernet(key).encrypt(text), key) == text)
            print("Passed")
            
            print("\t Passed")

        def all(self):
            print("\nTesting Crypt...\n")
            self.consturctor()
            self.get_handshake_pub()
            self.get_handshake_shared()
            self.get_pwd_key()
            self.get_session_key()
            self.auth()
            self.encrypt()
            self.decrypt()
            print("\nAll Tests passed!")

    test = CryptTester()
    test.all()