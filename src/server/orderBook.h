#ifndef ORDERBOOK_H_
#define ORDERBOOK_H_

#include "uthash.h"
#include "order.h"
#include <stdio.h>

typedef struct priceBucket{
	 int exchangeId;
	 struct order * curOrder;
	 UT_hash_handle hh;
}priceBucket;

typedef struct book {
    double price;
    priceBucket * pb;
    UT_hash_handle hh;
} book;

/**
* temporary set return type to void, to be decided further
*/
void addToBook(order * curOrder, book ** curBook);

/**
* temporary set return type to void, to be decided further
*/
void deleteFromBook(order * curOrder, book ** curBook);


#endif /* ORDERBOOK_H_ */
