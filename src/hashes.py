'''
Provides more convenient API for working with hashes
'''
from hashlib import sha256


class SHA256Hasher:
    '''
    Class for making salted SHA256
    '''
    def __init__(self, salt: str):
        '''
        Initializes salt
        '''
        self.salt: str = salt

    def hexdigest(self, string: str) -> str:
        '''
        Returns hashed string + salt
        '''
        return sha256(string.encode('utf-8') + self.salt.encode('utf-8')).hexdigest()

    def verify(self, plain: str, hashed: str) -> bool:
        '''
        Checks if hash of plain equals to hashed
        '''
        return self.hexdigest(plain) == hashed
