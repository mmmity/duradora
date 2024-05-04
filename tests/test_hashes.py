import unittest
from src.hashes import SHA256Hasher

class TestSHA256Hasher(unittest.TestCase):

    def test_hasher(self):
        hasher = SHA256Hasher(b'salt_from_Piter')

        self.assertEqual(hasher.hexdigest('sample'), hasher.hexdigest('sample'))
        self.assertTrue(hasher.verify('strongpassword', hasher.hexdigest('strongpassword')))
        self.assertFalse(hasher.verify('weakpassword', hasher.hexdigest('strongpassword')))

        hasher2 = SHA256Hasher(b'')
        self.assertEqual(hasher.hexdigest('hmm'), hasher2.hexdigest('hmmsalt_from_Piter'))
