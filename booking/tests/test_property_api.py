from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Property
from booking.serializers import PropertySerializer


PROPERTIES_URL = reverse('booking:property-list')


def detail_url(property_id):
    return reverse('booking:property-detail', args=[property_id])


class PublicPropertyApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_property(self):
        payload = {
            'name': 'Test house',
            'base_price': 10
        }
        res = self.client.post(PROPERTIES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        property_obj = Property.objects.get(id=res.data['id'])
        self.assertEqual(property_obj.name, payload['name'])
        self.assertEqual(property_obj.base_price, payload['base_price'])

    def test_retrieve_properties(self):
        Property.objects.create(name='Test House', base_price=10)
        Property.objects.create(name='Test Hotel', base_price=20)

        res = self.client.get(PROPERTIES_URL)
        properties = Property.objects.all().order_by('-created_at')
        serializer = PropertySerializer(properties, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_property(self):
        property_obj = Property.objects.create(name='Test House', base_price=10)
        payload = {
            'name': 'New name house'
        }
        url = detail_url(property_id=property_obj.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        property_obj.refresh_from_db()
        self.assertEqual(property_obj.name, payload['name'])

    def test_delete_property(self):
        property_obj = Property.objects.create(name='Test House', base_price=10)
        url = detail_url(property_id=property_obj.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        properties = Property.objects.all()
        self.assertFalse(properties.exists())
