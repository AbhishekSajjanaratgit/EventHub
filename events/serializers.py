from django.db import transaction
from django.db.models import F
from rest_framework import serializers

from .models import Event, Reservation

class EventSerializer(serializers.ModelSerializer):
    reservations_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id','title','venue','date','total_seats','available_seats','status','created_at','reservations_count']

    def get_reservations_count(self, obj):
        return obj.reservations.filter(status='confirmed').count()

    def validate(self, data):
        # On PATCH, a field may be missing, so fall back to the value already saved
        total = data.get('total_seats', getattr(self.instance, 'total_seats', None))
        available = data.get('available_seats', getattr(self.instance, 'available_seats', None))

        if total is not None and available is not None and available > total :
            raise serializers.ValidationError('available_seats cannot exceed total_seats.')

        return data

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'event', 'attendee_name', 'attendee_email','seats_reserved', 'status', 'created_at']
        read_only_fields = ['status', 'created_at']

    def validate_seats_reserved(self, value):
        if value < 1:
            raise serializers.ValidationError('Must reserve at least 1 seat.')

        return value

    def validate(self, data):
        # Early checks
        event = data['event']

        if event.status not in ('upcoming', 'ongoing'):
            raise serializers.ValidationError(f"cannot reserve seats for a {event.status} event.")

        if data['seats_reserved'] > event.available_seats:
            raise serializers.ValidationError(f"Only {event.available_seats} seat(s) available.")

        return data

    def create(self, validated_data):
        n = validated_data['seats_reserved']
        event = validated_data['event']

        with transaction.atomic():
            updated = Event.objects.filter(pk = event.pk,available_seats__gte = n).update(available_seats=F('available_seats') - n)

            if updated == 0:
                raise serializers.ValidationError(
                    {'non_field_errors' : ['Not enough seats available.']}
                )

            return Reservation.objects.create(**validated_data)
        