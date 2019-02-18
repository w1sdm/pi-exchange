package bot;

import java.io.IOException;
import java.net.Socket;

public class receiver extends Thread{
	Socket client = null;
	Object lock;
	sender s = null;
	public static int matchID = 0;
	int index;
	String initialInfo = "sell price: 0.000000, buy price: 0.000000\n";
	
	
	public receiver(Socket client, Object lock) {
		this.client = client;
		this.lock = lock;
	}
	
	
	public void run() {
		byte[] readResult=new byte[1024];
		while (true) {
			try {
				client.getInputStream().read(readResult);
			} catch (IOException e) {
				e.printStackTrace();
			}
			String echo = new String(readResult);
			//System.out.println(echo);
			if(echo.contains(initialInfo) || (echo.contains("-") && (sender.initialize)))  {
				//sender.status = 1;
				synchronized(main.lock){
					main.lock.notify();
					//System.out.println("notify");
				}
			}
			
			if (echo.contains("~")) {
				index = echo.indexOf("~order ID");
				matchID = Integer.valueOf(echo.substring(index+1, index+12));
				synchronized(main.lock){
					main.lock.notify();
					//System.out.println("notify");
				}		
			}
			//System.out.println("status: " + sender.status);
	
		}
		
		
		
		
	}
	
	
}
