from django.contrib.auth.models import User
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.test import APIClient

from django.test import TestCase
from .models import DataOperationModel


class SigninViewTest(APITestCase):
    def test_signin_view(self):
        username = 'admin1'
        password = '12345678'
        data = {
            'username': username,
            'password': password,
        }
        response = self.client.post('/api/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(username=username).exists())
        self.assertEqual(response.data, {'success': 'true'})


class LoginViewTestCase(APITestCase):
    def setUp(self):
        username = 'admin1'
        password = '12345678'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_login_success(self):
        url = reverse('/api/authorize/')

        data = {'username': self.username}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertEqual(response.data['message'], 'success')

    def test_login_invalid_username(self):
        url = reverse('authorize')

        data = {'username': 'nonexistentuser'}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], 'false')
        self.assertEqual(response.data['message'], 'Invalid Username')


class BasicOperationViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin1', password='12345678')
        self.client = APIClient()

    def test_get_data_list_authenticated(self):
        self.client.force_authenticate(user=self.user)
        DataOperationModel.objects.create(user=self.user, dictdata={'key': 'value'}, datasave='Test data')
        response = self.client.get('/api/dataoperation/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)

    def test_post_data_authenticated(self):
        self.client.force_authenticate(user=self.user)
        
        data = {
            'user': self.user.id,
            "dictdata": {
                "hello":1,
                "hello2":2
            },
            "datasave": "hello56"
        }
        
        response = self.client.post('/api/dataoperation/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_object = DataOperationModel.objects.get(id=response.data['id'])
        self.assertEqual(created_object.datasave, 'New test data')

    def test_delete_data_authenticated(self):
        self.client.force_authenticate(user=self.user)
        data_object = DataOperationModel.objects.create(user=self.user, dictdata={'key': 'value'}, datasave='Test data')
        data = {'data_id': data_object.id}
        response = self.client.delete('/your-api-endpoint-url/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(DataOperationModel.objects.filter(id=data_object.id, is_delete=True).exists(), True)