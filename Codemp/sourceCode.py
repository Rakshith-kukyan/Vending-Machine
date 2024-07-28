import board, busio, displayio, os, pwmio, time
import terminalio  # Just a font
import adafruit_ili9341
from adafruit_display_text import label
import digitalio
import microcontroller
from adafruit_motor import servo

SERVO_STATE_FILE = "/servo_state.txt"

def setup():
    global am1, am2, amount, display, splash, color_bitmap, color_palette, keyMatrix, t, u, w, noItems, avProd, loadProd
    global colPins, rowPins, rows, cols, current_text_group, j, count, v,idl,uart,idls,SERVO_ANGLES_SIZE
    uart = busio.UART(board.GP16, board.GP17, baudrate=9600)
    loadProd=0
    am1={}
    am2={}
    amount=0
    SERVO_ANGLES_SIZE = 6
    avProd= load_servo_state()
    print(avProd)
    displayio.release_displays()

    cs_pin, reset_pin, dc_pin, mosi_pin, clk_pin = board.GP18, board.GP19, board.GP20, board.GP15, board.GP14

    spi = busio.SPI(clock=clk_pin, MOSI=mosi_pin)

    display_bus = displayio.FourWire(spi, command=dc_pin, chip_select=cs_pin, reset=reset_pin)

    display = adafruit_ili9341.ILI9341(display_bus, width=240, height=320, rotation=270)
    splash = displayio.Group()
    display.root_group =splash

    color_bitmap = displayio.Bitmap(240, 320, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = 0x00FF00  # Bright Green

    # Variable to store the current text group
    current_text_group = None
    # Function to print text and remove previous text

    # Print the initial text

    j=0
    count=0
    v={}



    keyMatrix = [
        ["1", "2", "3", "Enter"],
        ["4", "5", "6", "Cancel"],
        ["7", "8", "9", "Delete"],
        ["*", "0", "#", "D"]
    ]

    t={'1':5, '2':25, '3':10, '4':15, '5':20, '6':50, "Enter":'Enter'}
    u={'1':1, '2':1, '3':1, '4':1, '5':1, '6':1}
    w={'1':39, '2':54, '3':69, '4':84, '5':99, '6':114, "Enter": 100}
    noItems={'1':0, '2':0, '3':0, '4':0, '5':0, '6':0}


    colPins = [board.GP9, board.GP8, board.GP7, board.GP6]
    rowPins = [board.GP5, board.GP4, board.GP1, board.GP0]

    rows = []
    cols = []

    # Set up row pins as outputs
    for pin in rowPins:
        row = digitalio.DigitalInOut(pin)
        row.direction = digitalio.Direction.OUTPUT
        rows.append(row)

    # Set up column pins as inputs with pull-down resistors
    for pin in colPins:
        col = digitalio.DigitalInOut(pin)
        col.direction = digitalio.Direction.INPUT
        col.pull = digitalio.Pull.DOWN
        cols.append(col)
    
    check_signal_strength()
    # Send AT command to set SMS mode to text
    send_at_command('AT+CMGF=1', 1)

def send_at_command(command, delay=1):
    uart.write(bytes(command + '\r\n', 'utf-8'))
    response = uart.read(256)  # Read up to 256 bytes
    if response:
        print(response.decode('utf-8'))
        decoded_response=str(response.decode('utf-8'))
    else:
        text = "\n\n\n\t  Service \n  Unavailable!"
        printtext(text,2,1,24)
        time.sleep(5)
        # Perform a software reset
        microcontroller.reset()
    return decoded_response

def check_signal_strength():
    send_at_command('AT+CSQ', 1)

def check_sms():
    # Send AT command to list all unread SMS
    response=send_at_command('AT+CMGL="REC UNREAD"', 3)
    if response:
        start_index = response.find("+CMGL:")
        if start_index != -1:
            end_index = response.find("\n", start_index)
            if end_index != -1:
                sms_data = response[start_index:end_index]
                sms_content_start = response.find("\n", end_index)
                sms_content = response[sms_content_start:].strip()
                return sms_content

def productLoaded():
    while len(splash) > 0:
        splash.pop()
    text = "\n\n\n\t Products \n    Reloading"
    printtext(text,2,1,24)
    products=[0]*6
    save_servo_state(products)
    serv= []
    serAngle=load_servo_state()
    j=0
    servo_pin = [board.GP13, board.GP12, board.GP11, board.GP10, board.GP3, board.GP2]
    for ser in servo_pin:
        pwm = pwmio.PWMOut(ser, frequency=50)
        serv.append(servo.Servo(pwm, min_pulse=580, max_pulse=2500))
        serv[j].angle = serAngle[j]
        j+=1
    time.sleep(5)
    # Perform a software reset
    microcontroller.reset()
    
def save_servo_state(serAngle):
    """Save the servo angles to non-volatile memory."""
    data = bytearray(SERVO_ANGLES_SIZE)
    for i, angle in enumerate(serAngle):
        data[i] = angle
    microcontroller.nvm[0:SERVO_ANGLES_SIZE] = data

def load_servo_state():
    """Load the servo angles from non-volatile memory."""
    data = microcontroller.nvm[0:SERVO_ANGLES_SIZE]
    return [int(angle) for angle in data]

def printtext(text,x,n,l):
    global current_text_group,v
    if (n==0 ):
        splash.remove(current_text_group)
        j=24
    text_group = displayio.Group(scale=x, x=11, y=l)
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
    text_group.append(text_area)  # Subgroup for text scaling
    splash.append(text_group)
    v[l]= text_group
    print(l,v)
    current_text_group = text_group
    
def starttext():
    bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
    splash.append(bg_sprite)

    # Draw a smaller inner rectangle
    inner_bitmap = displayio.Bitmap(230, 310, 1)
    inner_palette = displayio.Palette(1)
    inner_palette[0] = 0x000000  # Black
    inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=5, y=5)
    splash.append(inner_sprite)
    text = "\n\n\n\t  Welcome \n        to \n StationaryCart!!"
    printtext(text,2,1,24)
    time.sleep(2)
    j=0
    count=0
    v={}
    idl=""
    idls=[]
    
def scanStart():
    while True:
        key1 = scanKeypad()
        if key1=='Enter':
            break
    text = "Please Choose your \nproduct"
    printtext(text,2,0,24)
    time.sleep(0.2)

def scanKeypad():
    for rowIndex, row in enumerate(rows):
        row.value = True
        for colIndex, col in enumerate(cols):
            if col.value:
                row.value = False
                return keyMatrix[rowIndex][colIndex]
        row.value = False
    return None

def printKey():
    global amount,am1,am2,count,noItems,avProd,loadProd
    key = scanKeypad()
    j=0
    if key=="Enter":
        if count==0:
            for ob in am1:
                amount+=am1[ob]*am2[ob]
            text="\n\n\n\n\n\n\n\n\n\nTotal is: {}\nPress Enter to Continue".format(amount)
            printtext(text,2,1,j)
            count=count+1
        else:
            while len(splash) > 0:
                splash.pop()
            text="\n\n\nTotal is: {}\nPay through UPI\n..........\n..........\nPress Enter if done".format(amount)
            printtext(text,2,1,j)
            return 2
            
    elif key=="Cancel":
        # Perform a software reset
        microcontroller.reset()
    elif (avProd[0]==180 and key=='1') or (avProd[1]==180 and key=='2') or (avProd[2]==180 and key=='3') or (avProd[3]==180 and key=='4') or (avProd[4]==180 and key=='5') or (avProd[5]==180 and key=='6'):
        text="\n\n\n\n\n\n\n\n\n\nProduct: {} No more available".format(key)
        j=w[key]
        printtext(text,1,1,j)
        time.sleep(0.2)
        return 0
    elif key=='1' or key=='2' or key=='3' or key=='4' or key=='5' or key=='6':
        text="\n\n\n\nProduct: {} Price = {} X {}".format(key,t[key],u[key])
        j=w[key]
        am1[key]=int(t[key])
        am2[key]=int(u[key])
        if u[key]>1:
            splash.remove(v[j])
        u[key]+=1
        avProd[int(key)-1]+=30
        noItems[key]+=1
        print(text,key,w[key],j)
        printtext(text,1,1,j)
    elif key=='*':
        loadProd+=1
        if loadProd==8:
            productLoaded()
    time.sleep(0.2)
    return 0 
    
def payver():
    global amount,idl,idls,count
    while len(splash) > 0:
        splash.pop()
    printtext("Please wait\nwhile we verify\nthe payment",2,1,24)
    bal=0
    count=0
    payment=False
    while bal!=amount and count<30:
        sms_content=check_sms()  # Check for SMS messages
        if sms_content:
            bal_s=sms_content.find("BCB:Rs. ")
            if sms_content[bal_s:bal_s+8]=="BCB:Rs. ":
                bal_s=bal_s+8
                bal_e=sms_content.find(" credited")
                bal=float(sms_content[bal_s:bal_e])
                upi_s=sms_content.find("UPI/")
                upi_s=upi_s+12
                upi=int(sms_content[upi_s:upi_s+4])
                print(f"\nReceived Amount:\n{bal} Transation ID: {upi}\n")
                payment=True
        count+=1
    if payment==False:
        return False
    printtext("Enter Last 4 digits\nof Transaction ID",2,0,24)
    idl=""
    idls=[]
    while True:
        key = scanKeypad()
        if key=="Cancel":
            # Perform a software reset
            microcontroller.reset()
        elif key=="Delete":
            idls.pop()
            count=count-1
            idl=""
            for i in idls:
                idl=idl+i
            printtext(idl,2,0,95)
        elif key=="Enter" and len(idl)==4:
            if idl==str(upi) and amount==bal:
                return True
            else:
                return False
        elif key=='1' or key=='2' or key=='3' or key=='4' or key=='5' or key=='6' or key=='7' or key=='8' or key=='9' or key=='0':
            idl=idl+key
            idls.append(key)
            count=count+1
            printtext(idl,2,1,95)
        time.sleep(0.2)   
        
def dispense():
    global noItems
    serv= []
    serAngle=load_servo_state()
    j=0
    servo_pin = [board.GP13, board.GP12, board.GP11, board.GP10, board.GP3, board.GP2]
    for ser in servo_pin:
        pwm = pwmio.PWMOut(ser, frequency=50)
        serv.append(servo.Servo(pwm, min_pulse=580, max_pulse=2500))
        serv[j].angle = serAngle[j]
        j+=1
        print(serAngle)
    for i in range(6):
        key = str(i + 1)
        print(serAngle, noItems[key])
        while noItems[key] > 0 and serAngle[i] < 180:
            serAngle[i] += 30
            serv[i].angle = serAngle[i]
            noItems[key] -= 1
            save_servo_state(serAngle)  # Save the state after each move
            time.sleep(2.0)
        print(serAngle)
            
def main():
    while True:
        setup()
        starttext()
        scanStart()
        while True:
            result=printKey()
            if result==1:
                # Perform a software reset
                microcontroller.reset()
            elif result==2:
                if payver():
                    while len(splash) > 0:
                        splash.pop()
                    print("Payment verified successfully")
                    text = "\n\n\n\t  Payment \n    verified \n  successfully!!"
                    printtext(text,2,1,24)
                    dispense()
                    result==1
                    time.sleep(2)
                    # Perform a software reset
                    microcontroller.reset()
                else:
                    while len(splash) > 0:
                        splash.pop()
                    print("Payment verification failed")
                    text = "\n\n\n\t  Payment \n  verificaton \n       failed!!"
                    printtext(text,2,1,24)
                    result==1
                    time.sleep(2)
                    # Perform a software reset
                    microcontroller.reset()

main()

