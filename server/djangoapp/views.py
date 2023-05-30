from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarDealer
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
from django.contrib.auth.forms import UserCreationForm
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.

def about(request):
    return render(request, 'djangoapp/about.html')


def contact(request):
    return render(request, 'djangoapp/contact.html')

def login_request(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            messages.error(request, 'Invalid username or password')
    else:
        return render(request, 'djangoapp/login.html')
    return render(request, 'djangoapp/login.html')

def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

def registration_request(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_url')
    else:
        form = UserCreationForm()
    return render(request, 'djangoapp/registration.html', {'form': form})

def get_dealerships(request):
    if request.method == "GET":
        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/b4832bda-544b-4f53-a257-6325e7e8db39/dealership-package/get-dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return HttpResponse(dealer_names)

def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/b4832bda-544b-4f53-a257-6325e7e8db39/dealership-package/get-review-dealership"
        # Get dealer reviews from the URL
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        # Create a context dictionary with the reviews
        context = {'reviews': reviews}
        # Render the dealer details template with the context
        return render(request, 'djangoapp/dealer_details.html', context)

def add_review(request, dealer_id):
    if request.user.is_authenticated:
        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/b4832bda-544b-4f53-a257-6325e7e8db39/dealership-package/post-review-dealership"
        api_key = "ETeDf-4bTN0zUToVck_6ah9WoVSBjQJ3Igzpu7TMAXdI"
        review = {}
        review["time"] = datetime.utcnow().isoformat()
        review["dealership"] = dealer_id
        review["review"] = "i kinda like this place ngl"
        json_payload = {}
        json_payload["review"] = review
        post_request(url, data=json_payload, auth=HTTPBasicAuth('apikey', api_key))
    else:
        # Handle case where user is not authenticated
        pass