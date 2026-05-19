from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .models import Airplane, Airport, Booking, Flight, Passenger


class HomeView(TemplateView):
    # Simple landing page with links to major sections.
    template_name = "main/home.html"


class FlightListView(ListView):
    model = Flight
    template_name = "main/flight_list.html"
    context_object_name = "flights"
    queryset = Flight.objects.select_related(
        "airplane",
        "departure_airport",
        "arrival_airport",
    ).order_by("departure_time")


class FlightDetailView(DetailView):
    model = Flight
    template_name = "main/flight_detail.html"
    context_object_name = "flight"
    queryset = Flight.objects.select_related(
        "airplane",
        "departure_airport",
        "arrival_airport",
    ).prefetch_related("bookings__passenger")


class BookingCreateView(CreateView):
    model = Booking
    template_name = "main/booking_form.html"
    fields = ["passenger", "seat_number"]

    def dispatch(self, request, *args, **kwargs):
        # Load the selected flight first because the URL carries flight_id.
        self.flight = get_object_or_404(
            Flight.objects.select_related(
                "airplane",
                "departure_airport",
                "arrival_airport",
            ),
            pk=kwargs["flight_id"],
        )

        # Stop users early if the flight is already full.
        if self.flight.is_full:
            messages.error(request, "This flight is already full.")
            return redirect("flight-detail", pk=self.flight.pk)

        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["passenger"].queryset = Passenger.objects.order_by("name")
        return form

    def _attach_validation_errors(self, form, error):
        # Convert model validation errors into form errors.
        if hasattr(error, "message_dict"):
            for field_name, message_list in error.message_dict.items():
                target_field = None if field_name == "__all__" else field_name
                for message in message_list:
                    form.add_error(target_field, message)
            return

        for message in error.messages:
            form.add_error(None, message)

    def form_valid(self, form):
        # Flight is selected from the URL, not from the form.
        form.instance.flight = self.flight

        try:
            # Run Booking.clean() so we can enforce capacity checks here too.
            form.instance.full_clean()
        except ValidationError as error:
            self._attach_validation_errors(form, error)
            return self.form_invalid(form)

        messages.success(self.request, "Booking created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("flight-detail", kwargs={"pk": self.flight.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["flight"] = self.flight
        return context


class BaseModelListView(ListView):
    template_name = "main/model_list.html"
    context_object_name = "items"
    page_title = ""
    create_url_name = ""
    update_url_name = ""
    delete_url_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["create_url_name"] = self.create_url_name
        context["update_url_name"] = self.update_url_name
        context["delete_url_name"] = self.delete_url_name
        return context


class BaseModelFormMixin:
    template_name = "main/model_form.html"
    page_title = ""
    submit_label = "Save"
    success_url_name = "home"

    def get_success_url(self):
        return reverse_lazy(self.success_url_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["submit_label"] = self.submit_label
        return context


class BaseModelCreateView(BaseModelFormMixin, CreateView):
    pass


class BaseModelUpdateView(BaseModelFormMixin, UpdateView):
    submit_label = "Update"


class BaseModelDeleteView(DeleteView):
    template_name = "main/model_confirm_delete.html"
    page_title = ""
    success_url_name = "home"

    def get_success_url(self):
        return reverse_lazy(self.success_url_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        return context


class AirplaneListView(BaseModelListView):
    model = Airplane
    queryset = Airplane.objects.order_by("name")
    page_title = "Airplanes"
    create_url_name = "airplane-create"
    update_url_name = "airplane-update"
    delete_url_name = "airplane-delete"


class AirplaneCreateView(BaseModelCreateView):
    model = Airplane
    fields = ["name", "model", "capacity"]
    page_title = "Create Airplane"
    submit_label = "Create"
    success_url_name = "airplane-list"


class AirplaneUpdateView(BaseModelUpdateView):
    model = Airplane
    fields = ["name", "model", "capacity"]
    page_title = "Update Airplane"
    success_url_name = "airplane-list"


class AirplaneDeleteView(BaseModelDeleteView):
    model = Airplane
    page_title = "Delete Airplane"
    success_url_name = "airplane-list"


class AirportListView(BaseModelListView):
    model = Airport
    queryset = Airport.objects.order_by("code")
    page_title = "Airports"
    create_url_name = "airport-create"
    update_url_name = "airport-update"
    delete_url_name = "airport-delete"


class AirportCreateView(BaseModelCreateView):
    model = Airport
    fields = ["name", "city", "code"]
    page_title = "Create Airport"
    submit_label = "Create"
    success_url_name = "airport-list"


class AirportUpdateView(BaseModelUpdateView):
    model = Airport
    fields = ["name", "city", "code"]
    page_title = "Update Airport"
    success_url_name = "airport-list"


class AirportDeleteView(BaseModelDeleteView):
    model = Airport
    page_title = "Delete Airport"
    success_url_name = "airport-list"


class FlightManageListView(BaseModelListView):
    model = Flight
    queryset = Flight.objects.select_related(
        "airplane",
        "departure_airport",
        "arrival_airport",
    ).order_by("departure_time")
    page_title = "Flights (Management)"
    create_url_name = "flight-manage-create"
    update_url_name = "flight-manage-update"
    delete_url_name = "flight-manage-delete"


class FlightManageCreateView(BaseModelCreateView):
    model = Flight
    fields = [
        "flight_number",
        "airplane",
        "departure_airport",
        "arrival_airport",
        "departure_time",
        "arrival_time",
    ]
    page_title = "Create Flight"
    submit_label = "Create"
    success_url_name = "flight-manage-list"


class FlightManageUpdateView(BaseModelUpdateView):
    model = Flight
    fields = [
        "flight_number",
        "airplane",
        "departure_airport",
        "arrival_airport",
        "departure_time",
        "arrival_time",
    ]
    page_title = "Update Flight"
    success_url_name = "flight-manage-list"


class FlightManageDeleteView(BaseModelDeleteView):
    model = Flight
    page_title = "Delete Flight"
    success_url_name = "flight-manage-list"


class PassengerListView(BaseModelListView):
    model = Passenger
    queryset = Passenger.objects.order_by("name")
    page_title = "Passengers"
    create_url_name = "passenger-create"
    update_url_name = "passenger-update"
    delete_url_name = "passenger-delete"


class PassengerCreateView(BaseModelCreateView):
    model = Passenger
    fields = ["name", "email"]
    page_title = "Create Passenger"
    submit_label = "Create"
    success_url_name = "passenger-list"


class PassengerUpdateView(BaseModelUpdateView):
    model = Passenger
    fields = ["name", "email"]
    page_title = "Update Passenger"
    success_url_name = "passenger-list"


class PassengerDeleteView(BaseModelDeleteView):
    model = Passenger
    page_title = "Delete Passenger"
    success_url_name = "passenger-list"


class BookingManageListView(BaseModelListView):
    model = Booking
    queryset = Booking.objects.select_related("passenger", "flight").order_by("-booking_date")
    page_title = "Bookings (Management)"
    create_url_name = "booking-manage-create"
    update_url_name = "booking-manage-update"
    delete_url_name = "booking-manage-delete"


class BookingManageCreateView(BaseModelCreateView):
    model = Booking
    fields = ["passenger", "flight", "seat_number"]
    page_title = "Create Booking"
    submit_label = "Create"
    success_url_name = "booking-manage-list"


class BookingManageUpdateView(BaseModelUpdateView):
    model = Booking
    fields = ["passenger", "flight", "seat_number"]
    page_title = "Update Booking"
    success_url_name = "booking-manage-list"


class BookingManageDeleteView(BaseModelDeleteView):
    model = Booking
    page_title = "Delete Booking"
    success_url_name = "booking-manage-list"
    
