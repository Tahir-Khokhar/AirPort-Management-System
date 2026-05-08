from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Airplane(models.Model):
    # Basic airplane details.
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} ({self.model})"


class Airport(models.Model):
    # Airport code is unique (for example: JFK, DXB, LHR).
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.code} - {self.city}"


class Flight(models.Model):
    flight_number = models.CharField(max_length=20, unique=True)
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE,
        related_name="flights",
    )
    departure_airport = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="departing_flights",
    )
    arrival_airport = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="arriving_flights",
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        ordering = ["departure_time"]

    def clean(self):
        # A flight cannot leave and arrive at the same airport.
        if (
            self.departure_airport_id
            and self.arrival_airport_id
            and self.departure_airport_id == self.arrival_airport_id
        ):
            raise ValidationError("Departure and arrival airports must be different.")

        # Arrival must be later than departure.
        if self.departure_time and self.arrival_time and self.arrival_time <= self.departure_time:
            raise ValidationError("Arrival time must be later than departure time.")

    @property
    def booked_seats(self):
        return self.bookings.count()

    @property
    def remaining_seats(self):
        if not self.airplane_id:
            return 0
        return max(self.airplane.capacity - self.booked_seats, 0)

    @property
    def is_full(self):
        if not self.airplane_id:
            return True
        return self.booked_seats >= self.airplane.capacity

    def __str__(self):
        return f"{self.flight_number}: {self.departure_airport.code} → {self.arrival_airport.code}"


class Passenger(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.name} ({self.email})"


class Booking(models.Model):
    passenger = models.ForeignKey(
        Passenger,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    seat_number = models.CharField(max_length=10)
    booking_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-booking_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["flight", "seat_number"],
                name="unique_seat_per_flight",
            )
        ]

    def clean(self):
        # Only run capacity checks when a flight is selected.
        if not self.flight_id:
            return

        existing_bookings = Booking.objects.filter(flight=self.flight)
        if self.pk:
            existing_bookings = existing_bookings.exclude(pk=self.pk)

        # Prevent overbooking.
        if existing_bookings.count() >= self.flight.airplane.capacity:
            raise ValidationError("This flight is full. No more bookings can be created.")

    def __str__(self):
        return f"{self.passenger.name} - {self.flight.flight_number} ({self.seat_number})"
