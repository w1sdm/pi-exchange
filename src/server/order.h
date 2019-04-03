#ifndef ORDER_H_
#define ORDER_H_


// order's status: 0 in book; 1 matched; 2 cancel
typedef struct order
{
	double price;
	int amount;
	int orderId;
	int exchangeId;
	int status;
	int userId;
} order;

/**
* generate order with a generated key exchangeId and a initial status 0
* status: 0 not matched; 1 matched; 2 canceled
*/
order * generateOrder(double price, int amount, int orderId, int userId);

#endif /* ORDER_H_ */