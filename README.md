![alt text](https://i.imgur.com/k2kruGl.png "Logo Title Text 1")

# Pi Exchange 

This project is software developed for the Raspberry Pi 3 model B to try and emulate a low-latency exchange simulation that can handle a large quantity of buy/sell transactions. 

![alt text](https://i.imgur.com/6HUZLYM.png "Program Screenshot 1")

Getting Started
------
Both **Python** 3, **C **(*has to be run on raspberry pi / Linux*) and **Java** compilers will be needed to run each individual part.

***Linux***: 

**Run** the **install.sh script** to install the dependencies for the project, mainly a few libraries for python. 

Then **run the run.sh script** to run all the bits of the project together. Take into account that the **setup** of the **ports and IP configurations** will have to be done manually for now. 

***Windows***: 

A PowerShell script is currently in the works, but it shouldn't be to hard to install the python dependencies using `pip install feedparser` and `pip install psutil`. 

Then just compile and run the bot, server and GUI. Take into account that you have to edit the port numbers and IP configurations manually.

Server
------
#### 	Compile: gcc tcp_server.c exchange.c orderBook.c order.c -o server
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



## GUI



## Built With 

Python 3, Java SE 9 and C compiled with GCC. 



## Authors

- Vasilis Ieropolous

- Ke Chen

- Francisco Caeiro

- Julian Henjes

- Guanghao Yang

- Shen Huan 

  -----

  Thank you so much to **Refinitiv** for sponsoring the project.
