from datetime import datetime

from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Booking, PricingRule, Property
from booking.serializers import BookingSerializer


BOOKINGS_URL = reverse('booking:booking-list')


def create_property(**params):
    defaults = {
        'name': 'Big house in front of the beach',
        'base_price': 10
    }
    defaults.update(params)
    return Property.objects.create(**defaults)


def create_pricing_rule(property, **params):
    defaults = {
        'price_modifier': -10,
        'min_stay_length': 7,
        'fixed_price': None,
        'specific_day': None
    }
    defaults.update(params)
    return PricingRule.objects.create(property=property, **defaults)



def detail_url(booking_id):
    return reverse('booking:booking-detail', args=[booking_id])


class PublicBookingApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def create_booking(self, property, date_start, date_end):
        payload = {
            'date_start': date_start,
            'date_end': date_end,
            'property': property.id
        }
        return self.client.post(BOOKINGS_URL, payload)

    def test_create_booking_case_1(self):
        """
        Test creating a booking Case #1

        In this case the base price of the property is 10.
        The booking will be 10 days long.
        There is a rule that indicates for stays bigger than 7 days, a 10% discount should be applied.
        The final price should be 10 days * 10 base_price, minus a 10% discount => 90
        """
        property_obj = create_property()
        PricingRule.objects.create(
            property=property_obj,
            price_modifier=-10,
            min_stay_length=7
        )
        res = self.create_booking(
            property=property_obj,
            date_start='2022-01-01',
            date_end='2022-01-10'
        )
        booking = Booking.objects.get(id=res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(booking.property, property_obj)
        self.assertEqual(booking.final_price, 90)

    def test_create_booking_case_2(self):
        """
        Test creating a booking Case #2

        In this case the base price of the property is 10.
        The booking will be 10 days long.
        There is a rule that indicates for stays bigger than 7 days, a 10% discount should be applied.
        There is a second rule for stays bigger than 30 days, that rule should not apply,
        since the stay length is less than 30
        The final price should be 10 days * 10 base_price, minus a 10% discount => 90
        """
        property_obj = create_property()
        pricing_rules = [
            PricingRule(property=property_obj, price_modifier=-10, min_stay_length=7),
            PricingRule(property=property_obj, price_modifier=-20, min_stay_length=30)
        ]
        PricingRule.objects.bulk_create(pricing_rules)
        res = self.create_booking(
            property=property_obj,
            date_start='2022-01-01',
            date_end='2022-01-10'
        )
        booking = Booking.objects.get(id=res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(booking.property, property_obj)
        self.assertEqual(booking.final_price, 90)

    def test_create_booking_case_3(self):
        """
        Test creating a booking Case #3

        In this case the base price of the property is 10.
        The booking will be 10 days long.
        There is a rule that indicates for stays bigger than 7 days, a 10% discount should be applied.
        There is also a rule for 01-04-2022 with a fixed price of 20
        """
        property_obj = create_property()
        pricing_rules = [
            PricingRule(property=property_obj, price_modifier=-10, min_stay_length=7),
            PricingRule(property=property_obj, fixed_price=20, specific_day='2022-01-04')
        ]
        PricingRule.objects.bulk_create(pricing_rules)

        res = self.create_booking(
            property=property_obj,
            date_start='2022-01-01',
            date_end='2022-01-10'
        )
        booking = Booking.objects.get(id=res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(booking.property, property_obj)
        self.assertEqual(booking.final_price, 101)

    def test_create_booking_without_any_rule_to_apply(self):
        """
        Test creating a booking without any rule to apply
        """
        property_obj = create_property()
        PricingRule.objects.create(
            property=property_obj,
            price_modifier=-10,
            min_stay_length=30
        )

        res = self.create_booking(
            property=property_obj,
            date_start='2022-01-01',
            date_end='2022-01-10'
        )
        booking = Booking.objects.get(id=res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(booking.property, property_obj)
        self.assertEqual(booking.final_price, 100)

    def test_create_booking_with_specific_day_rule_to_apply(self):
        """
        Test creating a booking with specific day rule to apply
        """
        property_obj = create_property()
        PricingRule.objects.create(
            property=property_obj,
            price_modifier=-10,
            specific_day='2022-01-04'
        )

        res = self.create_booking(
            property=property_obj,
            date_start='2022-01-01',
            date_end='2022-01-10'
        )
        booking = Booking.objects.get(id=res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(booking.property, property_obj)
        self.assertEqual(booking.final_price, 99)

    def test_create_booking_with_specific_day_and_min_stay_length_rule(self):
        """
        Test creating a booking, when there are two rules that apply at the same time.
        Finally using the specific day rule
        """
        property_obj = create_property()
        pricing_rules = [
            PricingRule(property=property_obj, fixed_price=30, min_stay_length=1),
            PricingRule(property=property_obj, fixed_price=20, specific_day='2022-01-04')
        ]
        PricingRule.objects.bulk_create(pricing_rules)

        res = self.create_booking(
            property=property_obj,
            date_start='2022-01-04',
            date_end='2022-01-04'
        )
        booking = Booking.objects.get(id=res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(booking.property, property_obj)
        self.assertEqual(booking.final_price, 20)

    def test_create_booking_fixed_price_used(self):
        """
        Test creating a booking, when a specific rule has fixed_price and price_modifier
        at the same time.
        Finally using fixed price
        """
        property_obj = create_property()
        PricingRule.objects.create(
            property=property_obj,
            price_modifier=-10,
            fixed_price=50,
            specific_day='2022-01-04'
        )
        res = self.create_booking(
            property=property_obj,
            date_start='2022-01-01',
            date_end='2022-01-10'
        )
        booking = Booking.objects.get(id=res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(booking.property, property_obj)
        self.assertEqual(booking.final_price, 140)

    def test_create_booking_multiple_same_rule_diff_price_modifier(self):
        """
        Test creating booking, same rules with diff price modifier
        """
        property_obj = create_property()
        pricing_rules = [
            PricingRule(property=property_obj, price_modifier=-30, min_stay_length=7),
            PricingRule(property=property_obj, price_modifier=-10, min_stay_length=7)
        ]
        PricingRule.objects.bulk_create(pricing_rules)
        res = self.create_booking(
            property=property_obj,
            date_start='2022-01-01',
            date_end='2022-01-10'
        )
        booking = Booking.objects.get(id=res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(booking.property, property_obj)
        self.assertEqual(booking.final_price, 90)

    def test_create_booking_multiple_same_rule_fixed_price(self):
        """
        Test creating booking, same rules with diff fixed price
        """
        property_obj = create_property()
        pricing_rules = [
            PricingRule(property=property_obj, fixed_price=30, min_stay_length=7),
            PricingRule(property=property_obj, fixed_price=10, min_stay_length=7)
        ]
        PricingRule.objects.bulk_create(pricing_rules)
        res = self.create_booking(
            property=property_obj,
            date_start='2022-01-01',
            date_end='2022-01-10'
        )
        booking = Booking.objects.get(id=res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(booking.property, property_obj)
        self.assertEqual(booking.final_price, 300)

    def test_create_booking_multiple_specific_day_rules_fixed_price(self):
        """
        Test creating booking, same rules with diff fixed price
        """
        property_obj = create_property()
        pricing_rules = [
            PricingRule(property=property_obj, fixed_price=30, specific_day='2022-01-04'),
            PricingRule(property=property_obj, fixed_price=10, specific_day='2022-01-04')
        ]
        PricingRule.objects.bulk_create(pricing_rules)
        res = self.create_booking(
            property=property_obj,
            date_start='2022-01-04',
            date_end='2022-01-04'
        )
        booking = Booking.objects.get(id=res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(booking.property, property_obj)
        self.assertEqual(booking.final_price, 30)

    def test_create_booking_multiple_specific_day_rules_price_modifier(self):
        """
        Test creating booking, same rules with diff price modifier
        """
        property_obj = create_property()
        pricing_rules = [
            PricingRule(property=property_obj, price_modifier=-30, specific_day='2022-01-04'),
            PricingRule(property=property_obj, price_modifier=-10, specific_day='2022-01-04')
        ]
        PricingRule.objects.bulk_create(pricing_rules)
        res = self.create_booking(
            property=property_obj,
            date_start='2022-01-04',
            date_end='2022-01-04'
        )
        booking = Booking.objects.get(id=res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(booking.property, property_obj)
        self.assertEqual(booking.final_price, 9)

    def test_create_booking_multiple_min_stay_lenght_diff_lenght(self):
        property_obj = create_property()
        pricing_rules = [
            PricingRule(property=property_obj, fixed_price=5, min_stay_length=7),
            PricingRule(property=property_obj, fixed_price=8, min_stay_length=10)
        ]
        PricingRule.objects.bulk_create(pricing_rules)
        res = self.create_booking(
            property=property_obj,
            date_start='2022-01-01',
            date_end='2022-01-10'
        )
        booking = Booking.objects.get(id=res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(booking.property, property_obj)
        self.assertEqual(booking.final_price, 80)

    def test_retrieve_bookings(self):
        property_1 = create_property(name='Test House 1')
        property_2 = create_property(name='Test House 2')
        create_pricing_rule(property=property_1)
        create_pricing_rule(property=property_2)
        self.create_booking(
            property=property_1,
            date_start='2022-01-01',
            date_end='2022-01-10'
        )
        self.create_booking(
            property=property_2,
            date_start='2022-02-01',
            date_end='2022-02-10'
        )
        res = self.client.get(BOOKINGS_URL)
        bookings = Booking.objects.all().order_by('-created_at')
        serializer = BookingSerializer(bookings, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_booking_and_recalculate_final_price(self):
        property_obj = create_property()
        PricingRule.objects.create(
            property=property_obj,
            price_modifier=-10,
            min_stay_length=7
        )
        booking = Booking.objects.create(
            property=property_obj,
            date_start='2022-01-01',
            date_end='2022-01-10',
            final_price=90
        )
        payload = {
            'date_end': '2022-01-12'
        }
        url = detail_url(booking_id=booking.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        booking.refresh_from_db()
        self.assertEqual(booking.property, property_obj)
        self.assertEqual(
            booking.date_end,
            datetime.strptime(payload['date_end'], '%Y-%m-%d').date()
        )
        self.assertEqual(booking.final_price, 108)

    def test_delete_booking(self):
        property_obj = create_property()
        PricingRule.objects.create(
            property=property_obj,
            price_modifier=-10,
            min_stay_length=7
        )
        booking = Booking.objects.create(
            property=property_obj,
            date_start='2022-01-01',
            date_end='2022-01-10',
            final_price=90
        )
        url = detail_url(booking_id=booking.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Booking.objects.filter(id=booking.id).exists())
