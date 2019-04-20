![alt text](https://i.imgur.com/k2kruGl.png "Logo Title Text 1")

# Pi Exchange 

This project is software developed for the Raspberry Pi 3 model B to try and emulate a low-latency exchange simulation that can handle a large quantity of buy/sell transactions. 

![alt text](https://i.imgur.com/6HUZLYM.png "Program Screenshot 1")

Getting Started
------
Both **Python** 3, **C **(*has to be run on raspberry pi / Linux*) and **Java 10** compilers will be needed to run each individual part.

***Linux***: 

**Run** the **install.sh script** to install the dependencies for the project, mainly a few libraries for python and Java 10 JDK. 

Then **run the run.sh script** to run all the bits of the project together. Take into account that the **setup** of the **ports and IP configurations** will have to be done manually for now. 

**IF THE RUN SCRIPT DOES NOT WORK ON YOUR DEVICE DO:**
FOR THE SERVER
```
gcc tcp_server.c exchange.c order.c orderBook.c requestHandlr.c notification.c -o server -pthread
```
**RUN WITH**

```
./server
```

**RUN the gui with (edit IP address with ip address of server) 

```
python gui-v0.2.py
```
***Run the BOt with eclipse/inteli j


For now only the Bot gets configured from the configuration file , the programs needs to be run in this order

**SERVER** ---> **GUI** ---> **Bot** 

***Windows***: 

A **powershell** script is availible to install the python dependencies. Open powershell as admin and use `Set-ExecutionPolicy Unrestricted` to be able to run the script. **Alternatively** use `pip install feedparser` and `pip install psutil`. *(Note that this will only work if you have a pip already or a version of Python that comes with it.)*

The bot will need Java 10 JDK to be able to run on the machine you want. The server needs to be run on the Raspberry Pi using GCC.

Then just compile and run the bot, server and GUI. Take into account that you have to edit the port numbers and IP configurations manually.

Server
------
#### 	Compile: gcc tcp_server.c exchange.c order.c orderBook.c requestHandlr.c notification.c -o server -pthread
#### 	Run: ./server
#### 	Connect to server using ip and port 8890
*Note: the IP depends on whether server is running locally or remotely. For local: 127.0.0.1, remote: find the IP of device where server runs on*
	

#### 	Place an order with 5 parameters divided by the single character ",". 

#### 	The sequence of parameters are shown below:

1. single character p (place)

2. b stands for buy, s stands for sell

3. price

4. amount

5. order id (generated by client)

  

  **e.g. p,b,1.1,10,0***

#### 	Cancel order with 4 paramter divided by as single character ",". Sequence of parameters are as below:
1. single character c (cancel)

2. b stands for buy, s stands for sell

3. price

4. exchange id (generated by server)

  

  ***e.g. c,b,1.1,1***

#### 	Response from server

1. Status of current order

	* order ID: %d
  
	* exchange ID: %d
  
	* price: %f
  
	* amount: %d
  
	* status: %d

2. Status of previous order

	* user ID: %d

	* order ID : %d 

	* exchange ID: %d

	* price : %f 

	* amount: %d 

	* status: %d 

3. Best price

	* Sell price : %f

	* Buy price: %f

   
#### 	Note:
-  to try the function of server, simple complie client.c with command "gcc client.c -o client" and run with command "./client 127.0.0.1" and type parameters as described above with enter
-  current version of server only works well with 1 client, so please test with 1 client



## Bot
#### 	Connect to server using ip and port 8890
*Note: the IP depends on whether server is running locally or remotely. For local: 127.0.0.1, remote: find the IP of device where server runs on (ip address and port can be reset in config.txt under the same Java directory*

#### 	Running the BOT

**1. Initilization:**

After running, this BOT will automatically start with generating initial buy and sell orders (total amount of buy and sell orders to be generated can be reset by modifying the value of Initialization.number_stored).
	

**2. Providing market liquidity**

The prices in this market is always changing when the BOT generate a new order. Initially: 

	* best buy price == Gprice-Math.random()-Ggap
	* best sell price == Gprice+Math.random()+Ggap

By default, **Gprice == 100** and **Ggap == 1**, which means the initial gap between the best sell price and best buy price is about **2**. Due to the use of Math.random(), each order will likely to have a different price so that the price in the market is always changing. However, since the nature of trading is to "buy low, sell high", the buy price will be always reducing, and the sell price will be always increasing. Hence, a gap between the best sell price and the best buy price is maintained: when the gap between these two prices > **3**, this BOT will automatically cancel some orders and replace them with prices in the range of normal gaps.

#### 	How the BOT works

**1. Sending and receiving orders:**

All the orders must be synchronized and maintained in both the BOT and the server, which involves receiving / sending information of orders from / to the server. Two classes called **Sender** and **Receiver** are used to do the job. They are running concurrently by extending **Thread**, a mutex(lock) is used to allow them running in parallel.

#### 	Note:	
- the string format of placing / cancelling orders is the same as mentioned above in the **server** part.
- since the information of orders is received in the data type of String, a class called **Parse** is used to extract and change each order's **id, price, amount, exchangeID etc.** back to their original data type respectively (e.g. int) so that they can be stored in the BOT. The regular expression used is **"\\d+(\\.\\d+)?"** to parse the String

**2. Storing the information of orders:**

A class called **Store** is used to save the information in each order, in the form of:

	* id: %d
	* price: %f
	* amount: %d
	* exchangeId: %d
	
#### 	Note:	
- the constructor is: store(int id,  float price,  int amount)
- buy orders and sell orders are saved in 2 different Lists: buylist and selllist

## GUI



## Built With 

Python 3, Java SE 9 and C compiled with GCC. 



## Authors

- Vasilis Ieropolous (Group Leader / Gui)

- Ke Chen (Administrator / Server)

- Francisco Caeiro ( GitMaster / Server)

- Julian Henjes (Gui)

- Guanghao Yang (Bot)

- Shen Huan (Bot) 

  -----

  Thank you so much to **Refinitiv** for sponsoring the project.
