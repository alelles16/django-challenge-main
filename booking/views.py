from datetime import timedelta, date
from typing import List, Optional, Tuple

from rest_framework import viewsets, status
from rest_framework.response import Response

from core.models import Booking, PricingRule, Property
from booking import serializers


class PropertyViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.PropertySerializer
    queryset = Property.objects.all()


class PricingRuleViewSet(viewsets.ModelViewSet):\

    serializer_class = serializers.PricingRule
    queryset = PricingRule.objects.all()


class BookingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing bookings and calculating final prices.
    """

    serializer_class = serializers.BookingSerializer
    queryset = Booking.objects.all()

    def _get_range_dates(self, booking: Booking) -> List[date]:
        """
        Generate a list of dates for the booking duration.

        Args:
            booking: The booking instance.

        Returns:
            List of dates representing each day of the booking.
        """
        total_days = (booking.date_end - booking.date_start).days + 1
        return [booking.date_start + timedelta(days=num_days) for num_days in range(total_days)]

    def _valid_min_stay_rule(self, rule: PricingRule, total_days: int) -> bool:
        """
        Check if the given rule is valid based on minimum stay length.

        Args:
            rule: The pricing rule.
            total_days: Total duration of the booking.

        Returns:
            True if the rule is valid based on minimum stay length, otherwise False.
        """
        return rule.min_stay_length is not None and total_days >= rule.min_stay_length

    def _valid_specific_day_rule(self, rule: PricingRule, range_dates: List[date]) -> bool:
        """
        Check if the given rule is valid for a specific day.

        Args:
            rule: The pricing rule.
            day: The specific day to check.

        Returns:
            True if the rule is valid for the specific day, otherwise False.
        """
        return rule.specific_day is not None and rule.specific_day in range_dates

    def _get_rules_to_apply(self, booking: Booking, range_dates: List[date], total_days: int) -> List[PricingRule]:
        """
        Get applicable pricing rules for the booking.

        Args:
            booking: The booking instance.
            range_dates: List of dates for the booking duration.
            total_days: Total duration of the booking.

        Returns:
            List of applicable pricing rules.
        """
        pricing_rules = PricingRule.objects.filter(property=booking.property)
        return [
            rule for rule in pricing_rules
            if self._valid_min_stay_rule(rule, total_days) or self._valid_specific_day_rule(rule, range_dates)
        ]

    def _select_max_rule(self, applicable_rules: List[PricingRule]) -> Optional[PricingRule]:
        """
        Select the most relevant pricing rule from the list of applicable rules.
        """
        return max(
            applicable_rules,
            key=lambda rule: (
                rule.specific_day is not None,
                rule.min_stay_length or 0,
                rule.price_modifier or 0,
                rule.fixed_price or 0
            )
        ) if applicable_rules else None

    def _is_rule_applicable(self, rule: PricingRule, total_days: int, date: date) -> bool:
        """
        Check if the given rule is applicable for the specified total_days and date.
        """
        return (
            self._valid_min_stay_rule(rule, total_days) or
            (rule.specific_day is not None and rule.specific_day == date)
        )

    def _apply_rule(self, base_price: float, rule: PricingRule) -> float:
        """
        Apply the pricing rule to calculate the adjusted price based on the base price.
        """
        if rule.fixed_price is not None:
            return rule.fixed_price
        elif rule.price_modifier is not None:
            return base_price * (1 + rule.price_modifier / 100)
        else:
            return base_price

    def _get_final_price(self, booking: Booking) -> float:
        """
        Calculate the final price for the booking considering applicable pricing rules.

        Args:
            booking: The booking instance.

        Returns:
            The final price after applying pricing rules.
        """
        base_price = booking.property.base_price
        total_days = booking.stay_length
        range_dates = self._get_range_dates(booking)

        rules_to_apply = self._get_rules_to_apply(
            booking=booking,
            range_dates=range_dates,
            total_days=total_days
        )

        final_price = 0

        for date in range_dates:
            applicable_rules = [
                rule for rule in rules_to_apply
                if self._is_rule_applicable(rule, total_days, date)
            ]
            most_relevant_rule = self._select_max_rule(applicable_rules)

            if most_relevant_rule:
                final_price += self._apply_rule(base_price, most_relevant_rule)
            else:
                final_price += base_price

        return final_price

    def create(self, request, *args, **kwargs):
        """
        Create a new booking instance and calculate the final price.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer=serializer)

        booking = serializer.instance
        booking.final_price = self._get_final_price(booking)
        booking.save(update_fields=['final_price'])

        return Response(
            {
                'final_price': booking.final_price,
                'id': booking.id
            },
            status=status.HTTP_201_CREATED
        )
