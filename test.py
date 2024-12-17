import unittest
import json
from hashfunction import app
import random

class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
       self.app = app.test_client()
       self.app.testing = True

       # Test data
       random_number_str = str(random.randint(1, 9999999999))
       self.test_user = {
           "username": "testuserA_" + random_number_str,
           "password": "testpass123"
       }
       self.test_user2 = {
           "username": "testuserB_" + random_number_str,
           "password": "testpass1234"
       }
       self.test_user3 = {
           "username": "testuserC_" + random_number_str,
           "password": "testpass12345"
       }

   
    def test_create_account(self):
        # Test successful account creation
        response = self.app.post('/createAccount',
                                data=json.dumps(self.test_user),
                                content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('Account created successfully', response.json['message'])

        # Test missing data
        response = self.app.post('/createAccount',
                                data=json.dumps({"username": "testuser"}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
    

    def test_verify_account(self):
        # First create an account
        self.app.post('/createAccount',
                        data=json.dumps(self.test_user2),
                        content_type='application/json')
        
        # Test successful verification
        response = self.app.post('/verifyAccount',
                                data=json.dumps(self.test_user2),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Account is verified', response.json['message'])

        # Test invalid credentials
        invalid_user = {
            "username": self.test_user2["username"],
            "password": "wrongpass"
        }
        response = self.app.post('/verifyAccount',
                                data=json.dumps(invalid_user),
                                content_type='application/json')
        self.assertEqual(response.status_code, 401)
    
    def test_change_password(self):
        # First create an account
        self.app.post('/createAccount',
                        data=json.dumps(self.test_user3),
                        content_type='application/json')

        # Test successful password change
        change_pwd_data = {
            "username": self.test_user3["username"],
            "password": self.test_user3["password"],
            "newPassword": "newpass123"
        }
        response = self.app.post('/changePassword',
                                data=json.dumps(change_pwd_data),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Password changed successfully', response.json['message'])

        # Verify new password works
        verify_new_pwd = {
            "username": self.test_user3["username"],
            "password": "newpass123"
        }
        response = self.app.post('/verifyAccount',
                                data=json.dumps(verify_new_pwd),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Test invalid old password
        invalid_change = {
            "username": self.test_user3["username"],
            "password": "wrongpass",
            "newPassword": "newpass123"
        }
        response = self.app.post('/changePassword',
                                data=json.dumps(invalid_change),
                                content_type='application/json')
        self.assertEqual(response.status_code, 401)
        
if __name__ == '__main__':
   unittest.main()