from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import PricingRule, Property
from booking.serializers import PricingRuleSerializer


PRICING_RULES_URL = reverse('booking:pricingrule-list')


def detail_url(pricing_rule_id):
    return reverse('booking:pricingrule-detail', args=[pricing_rule_id])


def create_property(**params):
    defaults = {
        'name': 'Big house in front of the beach',
        'base_price': 10
    }
    defaults.update(params)
    return Property.objects.create(**defaults)


class PublicPricingRulesApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_pricing_rule(self):
        property_obj = create_property()
        payload = {
            'property': property_obj.id,
            'price_modifier': -10,
            'min_stay_length': 10
        }
        res = self.client.post(PRICING_RULES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        pricing_rule = PricingRule.objects.get(id=res.data['id'])
        self.assertEqual(pricing_rule.property, property_obj)
        self.assertEqual(pricing_rule.price_modifier, payload['price_modifier'])
        self.assertEqual(pricing_rule.min_stay_length, payload['min_stay_length'])

    def test_retrieve_pricing_rules(self):
        property_1 = create_property(name='Test House 1')
        property_2 = create_property(name='Test House 2')
        PricingRule.objects.create(
            property=property_1,
            price_modifier=-10,
            min_stay_length=7
        )
        PricingRule.objects.create(
            property=property_2,
            price_modifier=-10,
            min_stay_length=10
        )

        res = self.client.get(PRICING_RULES_URL)
        pricing_rules = PricingRule.objects.all().order_by('-created_at')
        serializer = PricingRuleSerializer(pricing_rules, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_pricing_rule(self):
        property_obj = create_property()
        pricing_rule = PricingRule.objects.create(
            property=property_obj,
            price_modifier=-10,
            min_stay_length=7
        )
        payload = {
            'min_stay_length': 10
        }
        url = detail_url(pricing_rule_id=pricing_rule.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        pricing_rule.refresh_from_db()
        self.assertEqual(pricing_rule.min_stay_length, payload['min_stay_length'])

    def test_delete_pricing_rule(self):
        property_obj = create_property()
        pricing_rule = PricingRule.objects.create(
            property=property_obj,
            price_modifier=-10,
            min_stay_length=7
        )
        url = detail_url(pricing_rule_id=pricing_rule.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        pricing_rules = PricingRule.objects.all()
        self.assertFalse(pricing_rules.exists())
