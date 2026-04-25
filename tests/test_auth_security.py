import unittest

from app.security.passwords import hash_password, verify_password
from app.security.tokens import create_access_token, decode_access_token


class AuthSecurityTestCase(unittest.TestCase):
    def test_password_hash_roundtrip(self) -> None:
        h = hash_password("correct horse battery staple")
        self.assertNotEqual(h, "correct horse battery staple")
        self.assertTrue(verify_password("correct horse battery staple", h))
        self.assertFalse(verify_password("wrong", h))

    def test_jwt_roundtrip(self) -> None:
        token = create_access_token(subject="123", extra_claims={"role": "UTILISATEUR"})
        payload = decode_access_token(token)
        self.assertEqual(payload["sub"], "123")
        self.assertEqual(payload["role"], "UTILISATEUR")
