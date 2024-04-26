from django_filters import rest_framework as filters

from core.models import Property, PricingRule, Booking
from reservations.settings import DATE_INPUT_FORMATS


class PropertyFilter(filters.FilterSet):

    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    base_price__gte = filters.NumberFilter(field_name='base_price', lookup_expr='gte')
    base_price__lte = filters.NumberFilter(field_name='base_price', lookup_expr='lte')

    class Meta:
        model = Property
        fields = ['name', 'base_price']


class PricingRuleFilter(filters.FilterSet):

    specific_day__gte = filters.DateFilter('specific_day', lookup_expr='gte', input_formats=DATE_INPUT_FORMATS)
    specific_day__lte = filters.DateFilter('specific_day', lookup_expr='lte', input_formats=DATE_INPUT_FORMATS)
    specific_day_range = filters.DateRangeFilter(field_name='specific_day', lookup_expr='exact')
    min_stay_length = filters.NumericRangeFilter(field_name='min_stay_length')

    class Meta:
        model = PricingRule
        fields = ['property', 'price_modifier', 'min_stay_length',
                  'fixed_price', 'specific_day']


class BookingFilter(filters.FilterSet):

    date_start__gte = filters.DateFilter('date_start', lookup_expr='gte', input_formats=DATE_INPUT_FORMATS)
    date_start__lte = filters.DateFilter('date_start', lookup_expr='lte', input_formats=DATE_INPUT_FORMATS)
    date_end__gte = filters.DateFilter('date_end', lookup_expr='gte', input_formats=DATE_INPUT_FORMATS)
    date_end__lte = filters.DateFilter('date_end', lookup_expr='lte', input_formats=DATE_INPUT_FORMATS)

    class Meta:
        model = Booking
        fields = ['property', 'date_start', 'date_end', 'final_price']
