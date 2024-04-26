from datetime import datetime

from rest_framework import serializers

from core.models import Booking, Property, PricingRule


class PropertySerializer(serializers.ModelSerializer):

    class Meta:
        model = Property
        fields = ['id', 'name', 'base_price']
        read_only_fields = ['id']

    def validate(self, data):
        base_price = data.get('base_price')
        if base_price is not None and base_price < 0:
            raise serializers.ValidationError("Base price cannot be negative.")
        return data


class BookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = ['id', 'property', 'date_start', 'date_end', 'final_price']
        read_only_fields = ['id', 'final_price']

    def validate(self, data):
        date_start = data.get('date_start')
        date_end = data.get('date_end')

        if date_start and date_start < datetime.now().date():
            raise serializers.ValidationError("Booking start date must be in the future.")

        if date_start and date_end and date_start > date_end:
            raise serializers.ValidationError("Booking end date must be after start date.")

        return data


class PricingRuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = PricingRule
        fields = ['id', 'property', 'price_modifier',
                  'min_stay_length', 'fixed_price', 'specific_day']
        read_only_fields = ['id']

    def validate(self, data):
        specific_day = data.get('specific_day')
        fixed_price = data.get('fixed_price')
        min_stay_length = data.get('min_stay_length')

        if specific_day and specific_day < datetime.now().date():
            raise serializers.ValidationError("Specific day must be in the future.")

        if fixed_price is not None and fixed_price < 0:
            raise serializers.ValidationError("Fixed price cannot be negative.")

        if min_stay_length is not None and min_stay_length < 0:
            raise serializers.ValidationError("Min stay length cannot be negative.")

        return data
