import http.client, urllib

def send_sms(message):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
      urllib.parse.urlencode({
        "token": "axwtyk5pobbvzj3w63u3qvora4scaw",
        "user": "ut6s9ekosuwi6x5bjef7k42r11c2h5",
        "message": message,
      }), { "Content-type": "application/x-www-form-urlencoded" })
    response = conn.getresponse()
    if response.status == 200:
        print("SMS sent successfully")
    else:
        print("Failed to send SMS")

send_sms("Appliaction Started")
