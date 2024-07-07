import time
import board
import busio

# Setup the UART connection
uart = busio.UART(tx=board.GP4, rx=board.GP5, baudrate=9600)

# Function to send AT command and wait for response
def send_at_command(command, timeout=1):
    uart.write((command + '\r\n').encode())
    time.sleep(timeout)
    response = uart.read(uart.in_waiting or 1).decode()
    return response

# Function to read all incoming data
def read_all():
    time.sleep(0.1)  # Give the module some time to respond
    data = uart.read(uart.in_waiting or 1).decode()
    return data

# Test if the module is responding
print("Testing SIM800L module...")
response = send_at_command("AT")
print(f"AT command response: {response}")

# Set SMS to text mode
print("Setting SMS text mode...")
response = send_at_command("AT+CMGF=1")
print(f"CMGF command response: {response}")

# Check for new SMS
def check_for_sms():
    response = send_at_command("AT+CMGL=\"REC UNREAD\"")
    if "REC UNREAD" in response:
        return response
    return None

# Function to parse SMS message
def parse_sms(sms_response):
    # Find the start of the message
    start_index = sms_response.find("+CMGL:")
    if start_index != -1:
        end_index = sms_response.find("\n", start_index)
        if end_index != -1:
            sms_data = sms_response[start_index:end_index]
            sms_content_start = sms_response.find("\n", end_index)
            sms_content = sms_response[sms_content_start:].strip()
            return sms_content
    return None

# Main loop to check for SMS
while True:
    print("Checking for new SMS...")
    sms_response = check_for_sms()
    if sms_response:
        print(f"SMS response: {sms_response}")
        sms_content = parse_sms(sms_response)
        if sms_content:
            print(f"Received SMS: {sms_content}")
            # Store the message in a variable
            received_message = sms_content
            print(f"Stored message: {received_message}")
        # Optionally delete the message after reading
        send_at_command('AT+CMGD=1,4')  # Delete all read messages
    time.sleep(10)  # Check for new messages every 10 seconds
