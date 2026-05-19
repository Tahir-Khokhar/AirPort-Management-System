from django.contrib import admin

from .models import Airplane, Airport, Booking, Flight, Passenger

@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ("name", "model", "capacity")
    search_fields = ("name", "model")

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "code")
    search_fields = ("name", "city", "code")

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = (
        "flight_number",
        "airplane",
        "departure_airport",
        "arrival_airport",
        "departure_time",
        "arrival_time",
    )
    search_fields = ("flight_number",)
    list_filter = ("departure_airport", "arrival_airport")

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ("name", "email")
    search_fields = ("name", "email")

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("passenger", "flight", "seat_number", "booking_date")
    search_fields = ("passenger__name", "flight__flight_number", "seat_number")
    list_filter = ("flight", "booking_date")
