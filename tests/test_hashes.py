'''
Tests for hashes module
'''
import unittest
from src.hashes import SHA256Hasher


class TestSHA256Hasher(unittest.TestCase):
    '''
    Class for testing SHA256Hasher
    '''
    def test_hasher(self):
        '''
        Basic functionality tests
        '''
        hasher = SHA256Hasher('salt_from_Piter')

        self.assertEqual(hasher.hexdigest('sample'), hasher.hexdigest('sample'))
        self.assertTrue(hasher.verify('strongpassword', hasher.hexdigest('strongpassword')))
        self.assertFalse(hasher.verify('weakpassword', hasher.hexdigest('strongpassword')))

        hasher2 = SHA256Hasher('')
        self.assertEqual(hasher.hexdigest('hmm'), hasher2.hexdigest('hmmsalt_from_Piter'))
