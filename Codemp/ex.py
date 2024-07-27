import board, busio, displayio, os, time
import terminalio  # Just a font
import adafruit_ili9341
from adafruit_display_text import label
import digitalio

am1={}
am2={}
amount=0
displayio.release_displays()

board_type = os.uname().machine

print(f"Board: {board_type}")

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
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]

t={'1':5, '2':25, '3':10, '4':15, '5':20, '6':50, "Enter":'Enter'}
u={'1':1, '2':1, '3':1, '4':1, '5':1, '6':1}
w={'1':39, '2':54, '3':69, '4':84, '5':99, '6':114, "Enter": 100}


colPins = [board.GP0, board.GP1, board.GP4, board.GP5]
rowPins = [board.GP6, board.GP7, board.GP8, board.GP9]

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
    
    text = "Please Choose your \nproduct"
    printtext(text,2,0,24)
    
    main()

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
    global amount,am1,am2,count
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
    elif key=="Cancel":
        while len(splash) > 0:
            splash.pop()
        reset()
    elif key:
        text="\n\n\n\nProduct: {} Price = {} X {}".format(key,t[key],u[key])
        j=w[key]
        am1[key]=int(t[key])
        am2[key]=int(u[key])
        if u[key]>1:
            splash.remove(v[j])
        u[key]+=1
        print(text,key,w[key],j)
        printtext(text,1,1,j)
    time.sleep(0.2)
    
def reset():
    global amount, am1, am2, count, u
    amount = 0
    am1 = {}
    am2 = {}
    count = 0
    u={'1':1, '2':1, '3':1, '4':1, '5':1, '6':1}
    while len(splash) > 0:
        splash.pop()
    current_text_group = None
    starttext()

def main():
    while True: 
        printKey()

starttext()


    
'''

  =="A":
        text="Total is: {}".format(amount)
        printtext(text,2,1)
    elif key=="B":
        text = "Please Choose your \nproduct"
        printtext(text,2,0)
    else
keyMatrix = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]

colPins = [board.GP0, board.GP1, board.GP2, board.GP3]
rowPins = [board.GP7, board.GP6, board.GP5, board.GP4]

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
    key = scanKeypad()
    if key:
        print("Key pressed is: {}".format(key))
    time.sleep(0.2)

while True:
    printKey()
 '''

