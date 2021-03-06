#CONSTANTS

#Socket Settings
#Set OVERRIDE_IP to None to read from config file
OVERRIDE_IP = None

#Enable/disable automatic price inputs
AUTO_PRICE = True

#Simulation Settings
START_BALANCE = 10000
START_STOCK_COUNT = 50

#Order form constraints
PRICE_LOWER_RANGE = 0
PRICE_UPPER_RANGE = 1000
PRICE_ACCURACY = 0.00001

QUANTITY_LOWER_RANGE = 0
QUANTITY_UPPER_RANGE = 10000

#Table Settings
FEEDWIDTH = 80
TABLE_WIDTH = 5
TABLE_HEIGHT = 20
CELL_WIDTH = 7

#Graph Settings
DELAY_BEFORE_AUTO_DRAW = 2000000
GRAPH_MAX_COORDS = 100
PADDING = 200
SIDE_PANEL_SIZE = 400

#Style Options
RELIEF = 'ridge'

import tkinter
import random
import feedparser
import socket
import threading
import platform
import psutil
import time
import os
import time
from functools import partial

#Setup initial variables

#Variable to store the balance locally
balance = START_BALANCE
virtualBalance = START_BALANCE
stockCount = START_STOCK_COUNT
virtualStockCount = START_STOCK_COUNT

#Variables for best buy and sell
bestBuy = None
bestSell = None

#Navigate up 2 folders to the config file
os.chdir("..")
os.chdir("..")

#Get info from the config file
with open('config.txt') as fin:
    # get lines of the file as list
    lines = fin.readlines()
    for line in lines:
        list_ = line.split(": ")
        if list_[0] == "IP-Address" :
            HOST_IP = list_[1].strip()
        elif list_[0] == "Port" :
            port = list_[1]
    fin.close()

HOST_IP = HOST_IP + ":" + port
#Override IP here if specified
if OVERRIDE_IP != None:
    HOST_IP = OVERRIDE_IP
else:
    print("IP Read from file: "+HOST_IP)

#Code to parse data from socket
#Possible Formats:

#-----------------
#<key>: <value>
#<key2>: <value2>
#<key3>: <value3>, time: <int>
#-----------------

def inferDataType(string):
    """Converts data type to best matching and returns"""
    if string.isalpha():
        return string
    elif '.' in string:
        return float(string)
    else:
        return int(string)

def parseToDict(data):
    """Convert data from socket into a dictionary object for easier manipulation"""
    dataDict = {}

    data = data.lstrip()

    #Split into lines
    data = data.split("\n")

    #For each line in the received data
    for d in data:

        #Ignore blank lines
        if d != '':

            #If not a separator line
            if d[0] != '-':

                #Remove | and ~ characters from the starts of keys
                if len(d) > 0:
                    if d[0] == '|' or d[0] == '~':
                        d = d[1:]

                #If multiple key/value pairs on one line, split
                d = d.split(", ")
                for pair in d:

                    #Separate key and value then save in dataDict
                    pair = pair.split(": ")
                    if len(pair) == 2:
                        dataDict[pair[0]] = inferDataType(pair[1])

    #Add a timestamp
    dataDict["time"] = time.time()

    #Return created dictionary object
    return dataDict

def splitIntoPackets(data):
    """Identify separate packets and return them"""
    packets = [""]
    for line in data.split("\n"):
        if line == '-'*18 or line == '~'*18:
            if packets[-1] != '':
                packets.append('')
        else:
            packets[-1] = packets[-1] + line + '\n'
    if packets[-1] == '':
        packets = packets[:-1]
    return packets

#Create window
root = tkinter.Tk()
win_width = root.winfo_screenwidth()
win_height = root.winfo_screenheight()

root.title("Stock Exchange GUI")
root.geometry(str(win_width)+"x"+str(win_height)+"+0+0")
root.attributes("-fullscreen",False)


#Create canvas frame
canvasFrame = tkinter.Frame(root,width=win_width-SIDE_PANEL_SIZE,height=(win_height-120))
canvasFrame.grid(row=0,column=0,rowspan=10)

#Create canvas for graph
canvas = tkinter.Canvas(canvasFrame,width=win_width-SIDE_PANEL_SIZE,height=(win_height-120)/2,bg='#001100')
canvas.grid(row=0,column=0)

#Create a canvas for the other graph
canvas2 = tkinter.Canvas(canvasFrame,width=win_width-SIDE_PANEL_SIZE,height=(win_height-120)/2,bg='#110000')
canvas2.grid(row=1,column=0)


#rss feed
feed = feedparser.parse('http://feeds.reuters.com/reuters/UKPersonalFinanceNews')
newsFrame = tkinter.Frame(canvasFrame, relief=tkinter.RIDGE,bd=3)
newsFrame.grid(row=2,column=0)

feedstr = ""
for entry in feed['entries']:
    feedstr = feedstr + entry['summary_detail']['value'].split("<")[0] + "  ---  "
news = tkinter.Label(newsFrame,text=feedstr,width=FEEDWIDTH,height=1,fg="#444444",font=("Courier"))
news.grid(row=0,column=0,padx=4,pady=4)

#Buy/Sell Form
orderFrame = tkinter.Frame(root, relief=RELIEF, bd=3, width=100)
orderFrame.grid(row=1,column=1,columnspan=2)

#Balance display
balanceText = tkinter.Label(orderFrame,text="Balance (£): {0} ({1})\nStock Count: {2} ({3})".format(balance, virtualBalance, stockCount, virtualStockCount))
balanceText.grid(row=0,column=0)

def updateBalanceOutput():
    global balance, virtualBalance, stockCount, virtualStockCount
    balanceText.config(text="Balance (£): {0} ({1})\nStock Count: {2} ({3})".format(balance, virtualBalance, stockCount, virtualStockCount))

orderLabel = tkinter.Label(orderFrame, text="Order Form", font=("",12))
orderLabel.grid(row=1,column=0)

#Buy/Sell Radiobuttons (only one can be active at a time)
bsFrame = tkinter.Frame(orderFrame,relief=RELIEF)
bsFrame.grid(row=2,column=0,pady=10,padx=10)

buyOrSell = tkinter.StringVar()
buyButton = tkinter.Radiobutton(bsFrame,text="Buy",indicatoron=False,value="buy",variable=buyOrSell,width=10,pady=4)
buyButton.grid(row=0,column=0)
sellButton = tkinter.Radiobutton(bsFrame,text="Sell",indicatoron=False,value="sell",variable=buyOrSell,width=10,pady=4)
sellButton.grid(row=0,column=1)

#Set default state to buy
buyButton.select()

#Price Input
priceFrame = tkinter.Frame(orderFrame)
priceFrame.grid(row=4,column=0,pady=10,padx=10)

priceLabel = tkinter.Label(priceFrame,width=10,text="Price (£): ")
priceLabel.grid(row=0,column=0)
priceInput = tkinter.Spinbox(priceFrame,from_=PRICE_LOWER_RANGE,to=PRICE_UPPER_RANGE,increment=PRICE_ACCURACY)  

def ValidateIfNum(self, s, S):
        # disallow anything but numbers
        valid = S.isdigit()
        if not valid:
            self.root.bell()
        return valid
        
priceInput.insert(0,0)
if AUTO_PRICE:
    priceInput.config(state=tkinter.DISABLED)
priceInput.grid(row=0,column=1)

#Quantity
quantityFrame = tkinter.Frame(orderFrame)
quantityFrame.grid(row=5,column=0,pady=10,padx=10)

quantityLabel = tkinter.Label(quantityFrame,width=10,text="Quantity: ")
quantityLabel.grid(row=0,column=0)
quantityInput = tkinter.Spinbox(quantityFrame,from_=QUANTITY_LOWER_RANGE,to=QUANTITY_UPPER_RANGE)
quantityInput.delete(0,tkinter.END)
quantityInput.insert(0,10)
quantityInput.grid(row=0,column=1)

#Place Order Button
confirmFrame = tkinter.Frame(orderFrame)
confirmFrame.grid(row=6,column=0,pady=10,padx=5)

confirmButton = tkinter.Button(confirmFrame,width=10,text="Confirm")
confirmButton.pack()
#Confirm button is bound to placeOrder() later on (it must first be defined)

#Create an error message Label
errorLabel = tkinter.Label(orderFrame,text="")
errorLabel.grid(row=7,column=0,columnspan=5)

#Order tables
tableFrame = tkinter.Frame(root, relief=RELIEF, bd=3, padx=10, pady=10)
tableFrame.grid(row=3,column=1)
tableLabel = tkinter.Label(tableFrame, text="Your Orders", pady=4, font=("",12))
tableLabel.grid(row=0,column=0, columnspan=2)

class Table():
    """Class to act as a table widget"""

    def __init__(self,width,height,frame,headers,cellWidth=CELL_WIDTH):
        """Initialise object and place Text widgets into the frame"""
        self.width,self.height,self.frame = width,height,frame
        self.headerTitles = headers
        self.headers = []
        self.rows = []
        self.cellWidth = cellWidth

        #Create the headers of the columns
        for x in range(self.width):
            self.headers.append(tkinter.Text(self.frame, width=self.cellWidth,height=1,bg="#eeeeef",fg="#666666"))
            self.headers[-1].grid(row=1,column=x)
            self.headers[-1].insert(tkinter.END,self.headerTitles[x])
            self.headers[-1].config(state=tkinter.DISABLED)


        #Create the cells of the table
        for y in range(1,self.height+1):
            self.rows.append([])
            for x in range(self.width):
                self.rows[-1].append(tkinter.Text(self.frame, width=self.cellWidth,height=1,bg="#eeeeef",fg="#666666"))
                self.rows[-1][-1].grid(row=y+1,column=x)
                self.rows[-1][-1].config(state=tkinter.DISABLED)

            #Create buttons to cancel orders
            self.rows[-1].append(tkinter.Button(self.frame,width=1,height=1,activebackground="#550000",activeforeground="#ffffff",bg="#aa0000",fg="#ffffff",text="X",font=("",6,"bold")))
            self.rows[-1][-1].config(command=partial(cancelOrder,y-1))
            self.rows[-1][-1].grid(row=y+1,column=x+1)


    #Clear the value in a cell
    def clear(self,column,row):
        self.rows[row][column].config(state=tkinter.NORMAL)
        self.rows[row][column].delete(1.0,tkinter.END)
        self.rows[row][column].config(state=tkinter.DISABLED)
        
    #Insert a value into a cell
    def insert(self,column,row,text):
        self.clear(column,row)
        self.rows[row][column].config(state=tkinter.NORMAL)
        self.rows[row][column].insert(tkinter.END,text)
        self.rows[row][column].config(state=tkinter.DISABLED)

    def get(self,column,row):
        return self.rows[row][column].get("1.0",tkinter.END)

def cancelOrder(row):
    """Cancel an order from the table"""
    #Get the ID from the table, and the order from the list
    id_ = table.get(0,row)
    print(id_)
    try:
        id_ = int(id_)
    except:
        return
    order = getOrder(id_)
    print(order)
    if order != None:
        #Ensure order is in book state
        if order["state"] == 0:
            packet = "{0},{1},{2},{3}".format('c',order["type"][0],order["price"],order["exID"])
            print("Sending: "+packet)
            c.send(packet)

table = Table(TABLE_WIDTH, TABLE_HEIGHT, tableFrame, ["ID","Type","Price","Qty","State"])

myOrders = []
#Example order

def getOrder(id_):
    """Get order information for the order with the provided client-side ID"""
    for order in myOrders:
        if order["id"] == id_:
            return order
    return None

def addOrder(id_,type_,price,quantity):
    global myOrders
    myOrders.append({"id":id_,"type":type_,"price":price,"quantity":quantity,"state":-1,"exID":None})

def updateOrderState(id_,newState):
    """Update the status of the order"""
    for i in range(len(myOrders)):
        if myOrders[i]["id"] == id_:
            myOrders[i]["state"] = newState

def getOrderState(id_):
    """Get the state of the order with the provided id"""
    for i in range(len(myOrders)):
        if myOrders[i]["id"] == id_:
            return myOrders[i]["state"]
    return None

def addExchangeID(id_,exID):
    """Add an exchange ID to the order - required for cancelling the order"""
    for i in range(len(myOrders)):
        if myOrders[i]["id"] == id_:
            myOrders[i]["exID"] = exID

def updateTable():
    global myOrders, table
    #Get most recent TABLE_HEIGHT amount of orders
    displayFrom = len(myOrders)-TABLE_HEIGHT
    displayFrom = max(displayFrom,0)
    row = 0
    for i in range(displayFrom,len(myOrders)):
        table.insert(0,row,myOrders[i]["id"])
        table.insert(1,row,myOrders[i]["type"])
        table.insert(2,row,myOrders[i]["price"])
        table.insert(3,row,myOrders[i]["quantity"])
        table.insert(4,row,{-1:"Waiting...",0:"Table",1:"Matched",2:"Cancel"}[myOrders[i]["state"]])
        row += 1
    while row < TABLE_HEIGHT:
        for i in range(5):
            table.insert(i,row,"-")
        row += 1

updateTable()

##examplePrice = 4 + random.random()*10
##for y in range(TABLE_HEIGHT):
##    table.insert(0,y,str(examplePrice))
##    table.insert(1,y,random.randint(1,6)*100)
##    examplePrice = examplePrice+random.random()*2

#created second frame with class
##tableFrame2 = tkinter.Frame(root, relief=RELIEF, bd=3, padx=30, pady=10)
##tableFrame2.grid(row=4,column=1)
##buyTableLabel = tkinter.Label(tableFrame2, text="Sell", pady=4, font=("",12))
##buyTableLabel.grid(row=0, column=0, columnspan=2)


##table2 = Table(TABLE_WIDTH, TABLE_HEIGHT, tableFrame2, ["Price","Quantity"])
##
##examplePrice = 4 + random.random()*10
##for y in range(TABLE_HEIGHT):
##    table2.insert(0,y,str(examplePrice))
##    table2.insert(1,y,random.randint(1,6)*100)
##    examplePrice = examplePrice+random.random()*2

#EXTRA STUFF
#CPU LABEL POWER
statsFrame = tkinter.Frame(root, relief=RELIEF, bd=3, width=200)
statsFrame.grid(row=5,column=1,columnspan=2)
cputext = tkinter.Label(statsFrame, text= "")
cputext.grid(row=0,column=0)
#FIGURE THIS OUT LATER

graphLock = threading.Lock()

#Secondary lock for second graph
graphLock2 = threading.Lock()

class Client():
    """A class to encapsulate client functionality"""
    def __init__(self,hostIP):
        self.hostIP = hostIP
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.host,self.port = self.hostIP.split(':')
        self.port = int(self.port)
        try:
            self.s.connect((self.host,self.port))
        except BaseException as e:
            print(e)
    def send(self,data):
        """Send string data to server"""
        self.s.sendall(data.encode())
    def receiveLoop(self):
        global bestBuy, bestSell
        """Listen to the server"""
        while True:
            msg = self.s.recv(2**16)
            msg = msg.decode()
            print(msg)
            for m in splitIntoPackets(msg):
                data = parseToDict(m)
                print(data)
                if "best sell" in data.keys():
                    #Update best sell price
                    bestSell = data["best sell"]
                    x = data["time"]
                    y = data["best sell"]
                    #Plot to graph
                    graphLock.acquire()
                    g.addCoords((x,y))
                    graphLock.release()
                    #Update the price input to match the best price
                    updatePriceInput()
                if "best buy" in data.keys():
                    #Update best buy price
                    bestBuy = data["best buy"]
                    x = data["time"]
                    y = data["best buy"]
                    #Plot to graph
                    graphLock2.acquire()
                    g2.addCoords((x,y))
                    graphLock2.release()
                    #Update the price input to match the best price
                    updatePriceInput()
                if "order ID" in data.keys() and "status" in data.keys():
                    #If no longer waiting for a response, free the button
                    if getOrderState(data["order ID"]) == -1:
                        freeButton()
                    updateOrderState(data["order ID"],data["status"])
                    updateTable()
                    #If it is matched
                    if data["status"] == 1:
                        for order in myOrders:
                            if order["id"] == data["order ID"]:
                                applyMatch(order)
                if "exchange ID" in data.keys() and "order ID" in data.keys():
                    addExchangeID(data["order ID"],data["exchange ID"])

class Graph():
    """Class to plot data to a canvas"""
    def __init__(self,canvasRef,maxCoords,padding=200):
        """Reference to a canvas object, max points of data shown simultaneously, canvas dimensions and padding for axis"""
        self.canvas = canvasRef
        self.values = []
        self.maxCoords = maxCoords
        self.CW, self.CH = self.canvas.winfo_reqwidth()-padding, self.canvas.winfo_reqheight()-padding
        self.padding = padding
    def addCoords(self,coords):
        """Add (x,y) to the list of coordinates, old values are removed according to maxCoords attribute"""
        self.values.append(coords)
        while len(self.values) > self.maxCoords:
            self.values.pop(0)
    def autoScroll(self):
        if len(self.values) >= 1:
            if time.time() - self.values[-1][0] < DELAY_BEFORE_AUTO_DRAW:
                self.addCoords((time.time(),self.values[-1][1]))
    def plot(self):
        """Plot stored coordinates to the canvas"""

        #Remove previous items
        self.canvas.delete(tkinter.ALL)

        if len(self.values) < 1:
            return

        #Establish minimums and maximums for the data
        minx = self.values[0][0]
        maxx = self.values[-1][0]
        miny = self.values[0][1]
        maxy = self.values[0][1]
        for c in self.values:
            if c[1] < miny:
                miny = c[1]
            elif c[1] > maxy:
                maxy = c[1]

        #Prevent the scales from being 0, but favour using only the necessary graph space
        if maxx-minx == 0:
            maxx+=0.5
            minx-=0.5
        if maxy-miny == 0:
            maxy+=0.5
            miny-=0.5

        #Calculate the scale
        scalex = maxx-minx
        scaley = maxy-miny

        #Plot all coordinates
        for c in range(len(self.values)):

            #Calculate colour based on increasing or decreasing value
            if c != len(self.values)-1:
                if self.values[c][1] > self.values[c+1][1]:
                    col = "#ff8888"
                elif self.values[c][1] < self.values[c+1][1]:
                    col = "#88ff88"
                else:
                    col = "#bebebe"

                #print("values[c] = {0}\nminx, maxx, miny, maxy = {1}, {2}, {3}, {4}\n scalex = {5}\nscaley = {6}".format(values[c],minx,maxx,miny,maxy,scalex,scaley))
                #Create line between this point and the next, applying calculations to scale and fit the points
                self.canvas.create_line(int(self.CW*((self.values[c][0]-minx)/scalex))+self.padding//2,
                                        self.CH-int(self.CH*((self.values[c][1]-miny)/scaley))+self.padding//2,
                                        int(self.CW*((self.values[c+1][0]-minx)/scalex))+self.padding//2,
                                        self.CH-int(self.CH*((self.values[c+1][1]-miny)/scaley))+self.padding//2,
                                        fill=col,width=2)

        #Write the current balance to the screen
        if len(self.values) > 1:

            c = len(self.values)-2
            if self.values[c][1] > self.values[c+1][1]:
                col = "#ff8888"
            elif self.values[c][1] < self.values[c+1][1]:
                col = "#88ff88"
            else:
                col = "#bebebe"

            #Label the balance at the text
            self.canvas.create_text(int(self.CW*((self.values[-1][0]-minx)/scalex))+self.padding//2 + 6,
                                            self.CH-int(self.CH*((self.values[-1][1]-miny)/scaley))+self.padding//2,
                                            fill=col,text="£"+str(round(self.values[-1][1],8)),anchor=tkinter.NW)

        #Create axis based on self.padding
        self.canvas.create_line(self.padding//2,self.padding//2,self.padding//2,self.CH+self.padding//2,fill="#ffffff",width=2)
        self.canvas.create_line(self.padding//2,self.CH+self.padding//2,self.CW+self.padding//2,self.CH+self.padding//2,fill="#ffffff",width=2)

        #Label axis with coordinates
        #X Axis
        #Convert time to string
        minx = time.ctime(minx)
        maxx = time.ctime(maxx)
        #Place text on canvas
        self.canvas.create_text(self.padding//2,self.CH+int(self.padding*3/4),text=minx,fill="#ffffff",font=("fixedsys",7),anchor=tkinter.W)
        self.canvas.create_text(self.CW+self.padding//2,self.CH+int(self.padding*3/4),text=maxx,fill="#ffffff",font=("fixedsys",7),anchor=tkinter.E)
        #Y Axis
        self.canvas.create_text(self.padding//4,self.padding//2,text=str(int(maxy)),fill="#ffffff",font=("fixedsys",7),anchor=tkinter.W)
        self.canvas.create_text(self.padding//4,self.CH+self.padding//2,text=str(int(miny)),fill="#ffffff",font=("fixedsys",7),anchor=tkinter.W)

        #Update canvas
        self.canvas.update()


#Create graphs
g = Graph(canvas,GRAPH_MAX_COORDS,padding=PADDING)
g2 = Graph(canvas2,GRAPH_MAX_COORDS,padding=PADDING)

c = Client(HOST_IP)
threading.Thread(target=c.receiveLoop).start()

#Plot function is called repeatedly in mainloop
def plot():
    #Draw to canvas
    graphLock.acquire()
    g.autoScroll()
    g.plot()
    graphLock.release()

    graphLock2.acquire()
    g2.autoScroll()
    g2.plot()
    graphLock2.release()

    #Call in next mainloop
    root.after(10,plot)

scrollAmount = 0
def scrollFeed():
    """Scroll through the feed"""
    global scrollAmount
    global feedstr
    #Update graphical element
    news.config(text=(" "*FEEDWIDTH + feedstr + " "*FEEDWIDTH)[scrollAmount:scrollAmount+FEEDWIDTH])
    scrollAmount += 1
    if scrollAmount+FEEDWIDTH > len(feedstr) + FEEDWIDTH*2:
        scrollAmount = 0
    root.after(70,scrollFeed)

#For generating client order IDs
class OrderID():
    currentID = 0
    def getNextOrderID():
        OrderID.currentID += 1
        return OrderID.currentID

def displayErrorOutput(text,col):
    """Update the error label"""
    errorLabel.config(text=text,fg=col)

#Validate buy/sell form input
def validateFormInput(quantity, price, type_):
    global virtualBalance, virtualStockCount
    #Make sure it is numeric data
    try:
        quantity = int(quantity)
        price = float(price)
    except ValueError:#Impossible conversion implies an invalid input
        displayErrorOutput("Error: Invalid/non-numerical input","#ff0000")
        return False
    #Potential other errors
    if quantity <= QUANTITY_LOWER_RANGE or quantity > QUANTITY_UPPER_RANGE:
        displayErrorOutput("Error: Quantity must be in range {0} <= quantity < {1}".format(QUANTITY_LOWER_RANGE, QUANTITY_UPPER_RANGE),"#ff0000")
        return False
    if price <= PRICE_LOWER_RANGE or price > PRICE_UPPER_RANGE:
        displayErrorOutput("Error: Price must be in range {0} <= price < {1}".format(PRICE_LOWER_RANGE, PRICE_UPPER_RANGE),"#ff0000")
        return False
    if type_ == "buy" and virtualBalance < float(price)*float(quantity):
        displayErrorOutput("Error: Insufficient funds: £{0} < £{1}".format(virtualBalance,float(price)*float(quantity)),"#ff0000")
        return False
    if type_ == "sell" and virtualStockCount < int(quantity):
        displayErrorOutput("Error: Insufficient stock: {0} < {1}".format(virtualStockCount,quantity),"#ff0000")
        return False
    displayErrorOutput("Success!","#00ff00")
    return True


#Form has been submitted
def placeOrder():
    global myOrders, virtualBalance, virtualStockCount
    #Block button until this order is resolved
    blockButton()
    order = {"orderType":buyOrSell.get(),"price":priceInput.get(),"quantity":quantityInput.get()}
    if AUTO_PRICE:
        order["price"] = str({"b": bestBuy, "s": bestSell}[order["orderType"][0]])
    #Format for the server
    if validateFormInput(order["quantity"],order["price"],order["orderType"]):
        #Get new unique clientside order ID
        id_ = OrderID.getNextOrderID()

        #Assemble the data for the server
        data = "p," + order["orderType"][0] + "," + str(order["price"]) + "," + str(order["quantity"]) + "," + str(id_)
        #Add the order to the local client records (table)
        addOrder(id_,order["orderType"],order["price"],order["quantity"])
        #Update virtual balances and stock levels
        if order["orderType"] == "buy":
            virtualBalance -= float(order["price"])*float(order["quantity"])
        if order["orderType"] == "sell":
            virtualStockCount -= int(order["quantity"])
        #Update graphical parts
        updateBalanceOutput()
        updateTable()
        #Send through socket
        print("Sending:",data)
        c.send(data)
    else:
        #Unblock the button
        freeButton()

def applyMatch(order):
    """Update balance and stock levels based on order"""
    global balance, stockCount, virtualBalance, virtualStockCount
    #If buy order placed, get the goods and pay from your balance
    if order["type"] == "buy":
        stockCount += int(order["quantity"])
        virtualStockCount += int(order["quantity"])
        balance -= float(order["price"])*float(order["quantity"])
    elif order["type"] == "sell":
        stockCount -= int(order["quantity"])
        balance += float(order["price"])*float(order["quantity"])
        virtualBalance += float(order["price"])*float(order["quantity"])
    updateBalanceOutput()

def blockButton():
    """Disable the button for the user"""
    confirmButton.config(state=tkinter.DISABLED)

def freeButton():
    """Enable the button for the user"""
    confirmButton.config(state=tkinter.NORMAL)    

def updatePriceInput():
    """Update price input graphical element"""
    global bestBuy, bestSell
    #Break if auto-pricing is off
    if not AUTO_PRICE:
        return
    #Enable editing, remove previous text
    priceInput.config(state=tkinter.NORMAL)
    priceInput.delete(0,tkinter.END)
    #If buy or sell, insert best buy or best sell price respectively
    if buyOrSell.get()[0] == 'b':
        if bestBuy != None:
            priceInput.insert(0,str(round(bestBuy,10)))
    elif buyOrSell.get()[0] == 's':
        if bestSell != None:
            priceInput.insert(0,str(round(bestSell,10)))
    #Disable editing
    priceInput.config(state=tkinter.DISABLED)

#Bind updatePriceInput function to the buy and sell buttons
buyButton.config(command=updatePriceInput)
sellButton.config(command=updatePriceInput)

def updateStats():
    cputext.config(text="CPU Usage: {0}%\nRAM Usage: {1}%".format(psutil.cpu_percent(),psutil.virtual_memory().percent))
    #Set the price to current buy or sell price
    root.after(500,updateStats)


#Configure confirm button to this function after the function has been defined
confirmButton.config(command=placeOrder)

def backgroundTasks():
    plot()
    scrollFeed()
    updateStats()

#Add plot to mainloop and hand over control to gui
root.after(1,backgroundTasks)
root.mainloop()
