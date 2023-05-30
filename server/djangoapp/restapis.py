import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth


def get_request(url, data=None, auth=None, **kwargs):
    print(data)
    print("GET from {} ".format(url))
    try:
        response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs, json=data, auth=auth)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data
    except:
        # If any error occurs
        print("Network exception occurred")

def post_request(url, data=None, auth=None):
    print(data)
    print("POST to {} ".format(url))
    try:
        response = requests.post(url, headers={'Content-Type': 'application/json'}, json=data, auth=auth)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data
    except:
        # If any error occurs
        print("Network exception occurred")


def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["docs"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    data = {'review': dealer_id}
    json_result = get_request(url, data=data)
    if json_result:
        reviews = json_result["docs"]
        for review_doc in reviews:
            review_obj = DealerReview(dealership=review_doc["dealership"], name=review_doc["name"], purchase=review_doc["purchase"], review=review_doc["review"], purchase_date=review_doc["purchase_date"], car_make=review_doc["car_make"], car_model=review_doc["car_model"], car_year=review_doc["car_year"], sentiment=review_doc.get("sentiment"), id=review_doc["id"])
            sentiment = analyze_review_sentiments(review_obj)
            review_obj.sentiment = sentiment
            results.append(review_obj)
    return results

def analyze_review_sentiments(dealerreview):
    # Set the URL and API key for the Watson NLU service
    url = "https://api.eu-de.natural-language-understanding.watson.cloud.ibm.com/instances/92f41ddb-9b07-417e-a500-4ef8ca23f5bb/v1/analyze"
    api_key = "ETeDf-4bTN0zUToVck_6ah9WoVSBjQJ3Igzpu7TMAXdI"

    # Set the parameters for the request
    params = {
        "text": dealerreview.review,
        "version": "2022-04-07",
        "features": {
            "keywords": {
                "sentiment": True
            }
        }
    }

    # Make the request to the Watson NLU service
    response = post_request(url, data=params, auth=HTTPBasicAuth('apikey', api_key))
    print(response)

    # Return the sentiment label from the response
    return response["keywords"][0]["sentiment"]["label"]