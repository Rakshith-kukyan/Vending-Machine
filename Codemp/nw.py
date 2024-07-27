import time
import wifi
import socketpool
import adafruit_requests

ssid = 'vivo 1820'
password = '11111111'

print("Connecting to Wi-Fi...")

# Connect to Wi-Fi
try:
    wifi.radio.connect(ssid, password)
    print("Connected to Wi-Fi")
except Exception as e:
    raise RuntimeError(f"Failed to connect to Wi-Fi: {e}")

# Get the IP address
ip_address = wifi.radio.ipv4_address
print(f"IP Address: {ip_address}")

# Initialize a socket pool and requests module
pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool)

# Make a GET request to Google
try:
    response = requests.get("http://httpbin.org/get")
    print("Response from httpbin:")
    print(response.text)
    response.close()
except Exception as e:
    print(f"Failed to get response from Google: {e}")


