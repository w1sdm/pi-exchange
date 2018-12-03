#include "requestHandlr.h"
#include <pthread.h>
#include <semaphore.h>

#define BUFFER_SIZE 1024

sem_t synchronize;
extern float buyPrice;
extern float sellPrice;

void handleRequest(int * conn)
{
    int sockfd = * conn;
    char buffer[BUFFER_SIZE];
    while(1)
    {
        memset(buffer,0,sizeof(buffer));
        int len = recv(sockfd, buffer, sizeof(buffer),0);
        if(strcmp(buffer,"exit\n")==0)
        {
            printf("client %d exited.\n",sockfd);
            break;
        }
        printf("client %d send:\n",sockfd);

        // split the string parameter by comma (see readme for more specific definition of parameter)
        char * delim = ",";
        char * pOc = strtok(buffer, delim); // first parameter, stands for place or cancel
        char * bOs = strtok( NULL, delim); // second parameter, stands for buy or sell

        order * temp = NULL;

        // decide what kind of request by compare 1st and 2nd parameter
        if(strcmp(pOc, "p") == 0){
            float price = atof(strtok( NULL, delim));
            int amount = atoi(strtok( NULL, delim));
            int orderId = atoi(strtok( NULL, delim));
            if(strcmp(bOs, "b") == 0){
                temp = placeBuyOrder(price, amount, orderId);
                printf("------------------\nplace buy order with \nexchange ID: %d \n", temp -> exchangeId);
                printf("price: %f \namount: %d \norder ID: %d \n\nbest buy price: %f, best sell price: %f\n------------------\n", price, amount, orderId, buyPrice, sellPrice);
            } else {
                temp = placeSellOrder(price, amount, orderId);
                printf("------------------\nplace sell order with \nexchange ID: %d \n", temp -> exchangeId);
                printf("price: %f \namount: %d \norder ID: %d \n\nbest buy price: %f, best sell price: %f\n------------------\n", price, amount, orderId, buyPrice, sellPrice);
            }
        } else{
            float price = atof(strtok( NULL, delim));
            int exchangeId = atoi(strtok( NULL, delim));
            if(strcmp(bOs, "b") == 0){
                temp = cancelBuyOrder(price, exchangeId);
                if(temp == NULL){
                    printf("------------------\norder not exist, please check again\n------------------\n");
                    send(sockfd, "order not exist, please check\n", 30, 0);
                    continue;
                }
                printf("------------------\ncancel buy order with \nexchange ID %d \n", temp -> exchangeId);
                printf("price:%f \namount: %d \norder ID:%d \n------------------\n", temp -> price, temp -> amount, temp -> orderId);
            } else {
                temp = cancelSellOrder(price, exchangeId);
                if(temp == NULL){
                    printf("------------------\norder not exist, please check again\n------------------\n");
                    send(sockfd, "order not exist, please check\n", 30, 0);
                    continue;
                }
                printf("------------------\ncancel sell order with \nexchange ID %d \n", temp -> exchangeId);
                printf("price:%f \namount: %d \norder ID:%d \n------------------\n", temp -> price, temp -> amount, temp -> orderId);
            }
        }

        // send specific information to server
        sprintf(buffer, "------------------\norder ID: %d\nexchange ID: %d\nprice: %f\namount: %d\nstatus: %d\n------------------\n",temp->orderId, temp->exchangeId, temp->price, temp->amount, temp->status);
        send(sockfd, buffer, sizeof(buffer), 0);

    }
    close(sockfd);
}
