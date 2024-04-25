from django_filters import rest_framework as filters

from core.models import Property, PricingRule, Booking


class PropertyFilter(filters.FilterSet):

    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    base_price__gte = filters.NumberFilter(field_name='base_price', lookup_expr='gte')
    base_price__lte = filters.NumberFilter(field_name='base_price', lookup_expr='lte')

    class Meta:
        model = Property
        fields = ['name', 'base_price']


class PricingRuleFilter(filters.FilterSet):

    specific_day = filters.DateRangeFilter(field_name='specific_day', lookup_expr='exact')

    class Meta:
        model = PricingRule
        fields = ['property', 'price_modifier', 'min_stay_length',
                  'fixed_price', 'specific_day']


class BookingFilter(filters.FilterSet):

    date_start__gte = filters.NumberFilter(field_name='date_start', lookup_expr='gte')
    date_start__lte = filters.NumberFilter(field_name='date_start', lookup_expr='lte')
    date_end__gte = filters.NumberFilter(field_name='date_end', lookup_expr='gte')
    date_end__lte = filters.NumberFilter(field_name='date_end', lookup_expr='lte')
    final_price__gte = filters.NumberFilter(field_name='final_price', lookup_expr='gte')
    final_price__lte = filters.NumberFilter(field_name='final_price', lookup_expr='lte')

    class Meta:
        model = Booking
        fields = ['property', 'date_start', 'date_end', 'final_price']
