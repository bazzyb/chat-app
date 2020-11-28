import hashlib
import pickle
import rsa
from cryptography.fernet import Fernet


def generate_asymmetric_keys():
    '''
        Assymetric keys are used to encrypt and decrypt the symmetric key,
        which is used for encrypting messages
        The public_key is also hashed, and the hash is passed with the public_key to the server

        Pool size dictates how many processes to run to build keys
        - More processes builds keys quicker
    '''

    public_key, private_key = rsa.newkeys(2048, poolsize=8)
    key_hash = hashlib.sha256(pickle.dumps(public_key)).hexdigest()
    return public_key, private_key, key_hash


def check_key_hash(key, passed_hash):
    '''
        The server generates it's own hash with the given key, and compares with the hash given
        This ensures that the key hasn't been tampered with during transmission
    '''

    key_hash = hashlib.sha256(key).hexdigest()
    if key_hash != passed_hash:
        raise Exception('Given hash does not match generated hash.')
    else:
        return True


def generate_symmetric_keys(public_key):
    '''
        The sym key is used to create the cipher via Fernet. 
        The cipher is what then encrypts each message
    '''

    sym_key = Fernet.generate_key()
    encrypted_sym_key = rsa.encrypt(sym_key, public_key)
    key_hash = hashlib.sha256(encrypted_sym_key).hexdigest()
    return sym_key, encrypted_sym_key, key_hash
