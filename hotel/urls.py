from django.urls import path

from hotel import views

app_name = "hotel"

urlpatterns = [
    path("", views.home, name="home"),
    path("rooms/", views.rooms, name="rooms"),
    path("rooms/<slug:slug>/", views.room_detail, name="room_detail"),
    path("book/", views.book, name="book"),
    path("book/availability/", views.booking_availability, name="booking_availability"),
    path("book/success/<str:reference>/", views.booking_success, name="booking_success"),
    path("contact/", views.contact, name="contact"),
    path("policy/<slug:slug>/", views.policy, name="policy"),
]
