import os
import sqlite3
from datetime import datetime
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import F

from .forms import LoadBalanceForm, ProfileEditForm, UserRegistrationForm
from .models import Booking, UserProfile


# Proje kök dizinine göre database dosyası yolu (güvenli)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "parking.db")


def redirect_to_login(request):
    if request.user.is_authenticated: 
        return redirect("main")
    return redirect("login")


@login_required()
def main(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    bookings = Booking.objects.filter(user=request.user)
    balance = get_user_balance(request.user)

    # parking.db dosyasından plakaları çek
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT plate, entry_time, exit_time, fee FROM parking")
        records = cursor.fetchall()
        conn.close()
    except Exception as e:
        print("Veritabanına bağlanırken hata oluştu:", e)
        records = []

    # Kayıtları işleyerek rezervasyon oluştur
    for plate, entry_time, exit_time, fee in records:
        profiles = UserProfile.objects.filter(car_plate=plate)
        if profiles.exists():
            for profile in profiles:
                user = profile.user
                start_time = datetime.strptime(entry_time, "%Y-%m-%d %H:%M:%S")
                end_time = datetime.strptime(exit_time, "%Y-%m-%d %H:%M:%S") if exit_time else None

                existing = Booking.objects.filter(
                    user=user,
                    car_plate=plate,
                    start_time=start_time,
                    end_time=end_time
                ).exists()

                if not existing:
                    Booking.objects.create(
                        user=user,
                        car_plate=plate,
                        start_time=start_time,
                        end_time=end_time,
                        amount=fee,
                        paid=False,
                    )
                    print(f"Yeni rezervasyon oluşturuldu: {plate}")
                else:
                    print(f"Zaten mevcut rezervasyon: {plate}")
        else:
            print(f"Plaka {plate} için kullanıcı bulunamadı.")

    return render(request, "main.html", {"balance": balance, "bookings": bookings})


def get_user_balance(user):
    try:
        profile = UserProfile.objects.get(user=user)
        return profile.balance
    except UserProfile.DoesNotExist:
        return 0


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            car_plate = form.cleaned_data["car_plate"]
            UserProfile.objects.create(user=user, car_plate=car_plate)

            return redirect("login")
    else:
        form = UserRegistrationForm()
    return render(request, "register.html", {"user_form": form})


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("main")
    return render(request, "login.html")


@login_required
def pay_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    profile = get_object_or_404(UserProfile, user=request.user)

    if profile.balance >= Decimal(booking.amount):
        # 1. Bakiyeyi düş
        profile.balance -= Decimal(booking.amount)
        profile.save()

        # 2. Booking'i ödenmiş olarak işaretle
        booking.paid = True
        booking.save()

        # 3. Profili güncelle (veritabanından tekrar al)
        profile.refresh_from_db()
        return redirect("main")

    else:
        # Yetersiz bakiye varsa hata mesajı gönder
        return render(request, "main.html", {
            "balance": profile.balance,
            "bookings": Booking.objects.filter(user=request.user),
            "error": "Yetersiz bakiye"
        })


def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect("login")


@login_required()
def load_balance(request):
    if request.method == "POST":
        form = LoadBalanceForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]

            # Bakiyeyi güncelle
            profile = get_object_or_404(UserProfile, user=request.user)
            profile.balance += Decimal(amount)
            profile.save()

            return redirect("main")
    else:
        form = LoadBalanceForm()
    return render(request, "load_balance.html", {"form": form})



@login_required()
def profile_edit(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        form = ProfileEditForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            request.user.first_name = form.cleaned_data["first_name"]
            request.user.last_name = form.cleaned_data["last_name"]
            request.user.save()

            profile.car_plate = form.cleaned_data["car_plate"]
            profile.save()
            return redirect("main")
    else:
        form = ProfileEditForm(instance=profile, user=request.user)
    return render(request, "profile_edit.html", {"profile_form": form})
