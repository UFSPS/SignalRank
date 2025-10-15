# Example request to Open Trivia #####################

"""
import requests
# More documentation: https://publicapi.dev/open-trivia-api

API_URL = "https://opentdb.com/api_config.php"
parameters = {
    "amount" : 10,
    "encode" : "base64"
} 

try:
    response = requests.get(API_URL, params=parameters)
    data = response.json()
    if (data["response_code"] == 5):
        print("Rate limit occured, too many requests!")

except requests.execptions.RequestException as e:
    print("Error occurred during API request: {e}")
"""