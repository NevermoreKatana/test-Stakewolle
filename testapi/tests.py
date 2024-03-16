from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from testapi.models import ReferralCode, Referral
from testapi.serializers import UserSerializer
from django.contrib.auth import get_user_model
import json
from dateutil import parser


VALID_USERNAME = 'katana'
VALID_EMAIL = 'crymorebch@gmail.com'
VALID_REF_CODE = 'testing'
INVALID_EMAIL = 'aaassddda222h@gmail.com'
PASSWORD ='nevermore'
USER_MODEL = get_user_model()

class UserRegistrationViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_test = USER_MODEL.objects.create_user(
            username=VALID_USERNAME + '1',
            password=PASSWORD + '1',
            email=VALID_EMAIL)
        
        date_object = parser.parse('2024.12.22')
        expiry_date = date_object.strftime("%Y-%m-%d")
        
        ReferralCode.objects.create(
            user = self.user_test,
            code=VALID_REF_CODE,
            expiry_date=expiry_date,
            is_active=True)
        
        self.valid_payload = {
            'username': VALID_USERNAME,
            'password': PASSWORD,
            'email': VALID_EMAIL,
        }
        self.invalid_payload = {
            'username': VALID_USERNAME,
            'password': PASSWORD,
            'email': INVALID_EMAIL,
        }
        self.valid_ref_payload = {
            'username': VALID_USERNAME,
            'password': PASSWORD,
            'email': VALID_EMAIL,
            'referral_code': VALID_REF_CODE
        }

            
        self.invalid_ref_payload = {
            'username': VALID_USERNAME,
            'password': PASSWORD,
            'email': VALID_EMAIL,
            'referral_code': '111'
        }

    def test_create_valid_user(self):
        response = self.client.post(
            reverse('registration'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Successfully created a new user without referral code')
        

    def test_create_invalid_user(self):
        response = self.client.post(
            reverse('registration'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid email address')
    
    def test_create_without_data(self):
        response = self.client.post(
            reverse('registration'),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['username'][0], 'This field is required.')
        self.assertEqual(response.data['password'][0], 'This field is required.')
        self.assertEqual(response.data['email'][0], 'This field is required.')
        
    def test_two_username(self):
        response = self.client.post(
            reverse('registration'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        response1 = self.client.post(
            reverse('registration'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response1.data['username'][0], 'A user with that username already exists.')
    
    def test_invalid_ref(self):
        response = self.client.post(
            reverse('registration'),
            data=json.dumps(self.invalid_ref_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid referral code')
    
    def test_valid_ref(self):
        response = self.client.post(
            reverse('registration'),
            data=json.dumps(self.valid_ref_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Successfully created a new user with referral code')


class UserLoginViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = USER_MODEL.objects.create_user(
            username=VALID_USERNAME,
            password=PASSWORD,
            email=VALID_EMAIL)
        
        self.valid_payload = {
            'username': VALID_USERNAME,
            'password': PASSWORD,
        }
        self.invalid_payload = {
            'username': 'invaliduser',
            'password': 'invalidpassword'
        }

    def test_valid_login(self):
        response = self.client.post(
            reverse('login'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_invalid_login(self):
        response = self.client.post(
            reverse('login'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid Username/Password')
        
    def test_invalid_body(self):
        response = self.client.post(
            reverse('login'),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid Username/Password')


class ReferralCodeViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.invalid_client = APIClient()
        self.invalid_user = USER_MODEL.objects.create_user(
            username= VALID_USERNAME + '1',
            password=PASSWORD + '1',
            email=INVALID_EMAIL)
        
        self.user = USER_MODEL.objects.create_user(
            username=VALID_USERNAME,
            password=PASSWORD,
            email=VALID_EMAIL)
        
        self.invalid_client.force_authenticate(user=self.invalid_user)
        self.client.force_authenticate(user=self.user)
        self.referral_code = ReferralCode.objects.create(user=self.user, expiry_date='2024-12-31')

    def test_get_referral_code(self):
        response = self.client.get(reverse('ref-code'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Referral code has been sent to the email')
    
    def test_invalid_ref_code(self):
        response = self.invalid_client.get(reverse('ref-code'))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'No active code found for this user')
    

    def test_post_referral_code(self):
        valid_payload = {
            'expiry_date': '2024-12-31'
        }
        response = self.client.post(
            reverse('ref-code'),
            data=json.dumps(valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user'], self.user.id)
        
    def test_invalid_data_post_referral_code(self):
        valid_payload = {
            'expiry_date': '2022-12-31'
        }
        response = self.client.post(
            reverse('ref-code'),
            data=json.dumps(valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Expiry date must be in the future")


    def test_invalid_post_referral_code(self):

        response = self.client.post(
            reverse('ref-code'),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Expiry date is required')

    def test_delete_referral_code(self):
        response = self.client.delete(reverse('ref-code'))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], 'Code successfully delete')
    
    def test_invalid_del_ref_code(self):
        response = self.invalid_client.delete(reverse('ref-code'))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], "No active code found")


class ReferralInfoViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username=VALID_USERNAME,
            password= PASSWORD,
            email = VALID_EMAIL
            )
        self.client.force_authenticate(user=self.user)
        self.referral_user = get_user_model().objects.create_user(
            username='referraluser',
            password='testpassword',
            
            )
        self.referral_code = ReferralCode.objects.create(user=self.user, expiry_date='2024-12-31')
        self.referral = Referral.objects.create(referrer=self.user, referral=self.referral_user)

    def test_get_referral_info(self):
        response = self.client.get(reverse('ref-info'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['referrals'], ['referraluser'])