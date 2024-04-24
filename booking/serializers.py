from rest_framework import serializers

from core.models import Booking, Property, PricingRule


class PropertySerializer(serializers.ModelSerializer):

    class Meta:
        model = Property
        fields = ['id', 'name', 'base_price']
        read_only_fields = ['id']


class BookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = ['id', 'property', 'date_start', 'date_end', 'final_price']
        read_only_fields = ['id', 'final_price']


class PricingRuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = PricingRule
        fields = ['id', 'property', 'price_modifier',
                  'min_stay_length', 'fixed_price', 'specific_day']
        read_only_fields = ['id']
