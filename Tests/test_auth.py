import unittest
from Backend.authentication import authenticate_gmail
import os

class TestAuthentication(unittest.TestCase):
    
    def test_authentication(self):
        # Run the authentication process
        service = authenticate_gmail()
        
        # Check if the service object is created and token.pickle exists
        self.assertIsNotNone(service)
        self.assertTrue(os.path.exists('token.pickle'), "token.pickle not created")

if __name__ == "__main__":
    unittest.main()
