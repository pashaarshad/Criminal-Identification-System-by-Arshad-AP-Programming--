import http.client
import urllib
import os
import base64

def send_sms_with_image(message, image_path=None):
    try:
        params = {
            "token": "axwtyk5pobbvzj3w63u3qvora4scaw",
            "user": "ut6s9ekosuwi6x5bjef7k42r11c2h5",
            "message": message
        }
        
        # If image path is provided, encode and attach it
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode()
                params["attachment_base64"] = encoded_image
                params["attachment_type"] = "image/png"

        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
                    urllib.parse.urlencode(params),
                    {"Content-type": "application/x-www-form-urlencoded"})
        
        response = conn.getresponse()
        if response.status == 200:
            print("Message sent successfully with image")
        else:
            print(f"Failed to send message: {response.status} - {response.reason}")
            
    except Exception as e:
        print(f"Error sending message: {str(e)}")

send_sms_with_image("Application Started", "path/to/image.png")
