
#include "server.h"
#include "game.h"

#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>



#define PORT 8080
#define MAX 1024

int game_loop(int connfd, int game)
{   
    game_t * curr_game = NULL;
    server_t * resp_packet = NULL;
    server_t * recv_packet = NULL;
    uint8_t starting_x = 4;
    uint8_t starting_y = 9;
    char err_msg[] = "Game Failed To Register!\n";
    char register_success[] = "Registration Successful!\n";
    int connected = 0;
    while (1 == game)
    {
        char buff[MAX] = {0};
        uint8_t resp_buff[MAX] = {0};
        ssize_t bytes_received = 0;
        ssize_t bytes_sent = 0;
        bytes_received = recv(connfd, buff, sizeof(buff), 0);
        
        if (0 == bytes_received)
        {
            printf("Connection closed by client\n");
            exit(0);
        }

        switch(buff[0])
        {
            case REQ_REGISTER:
                

                recv_packet = deserialize_packet(buff, bytes_received);

                if (NULL == recv_packet)
                {
                    perror("Failed to deserialize packet!\n");
                    break;
                }
                
                printf("RECV_PACKET TYPE : %d\n", recv_packet->type);
                printf("RECV LEN : %d \n", recv_packet->length);
                printf("RECV Data : %s\n", recv_packet->data);
                curr_game = calloc(1, sizeof(game_t));

                printf("Below initalization of game struct\n");
                    if (NULL == curr_game)
                    {
                        perror("Failed to initialize an new game!\n");
                        //need to call failure here
                        resp_packet = create_packet(RESP_ERROR, strlen(err_msg) + 1, err_msg);
                        if (NULL == resp_packet)
                        {
                            perror("failed to create response packet!\n");
                            break;
                        }
                        printf("made the packet\n");
                        if (serialize_packet(resp_packet, resp_buff))
                        {
                            bytes_sent = send(connfd, resp_buff, strlen(resp_buff) + 1, 0);

                            if (-1 == bytes_sent)
                            {
                                perror("Failed to send data to client!\n");
                                break;
                            }
                            printf("Error Msg sent to client\n");
                            break;
                        }
                        break;
                    }
                memset(curr_game->level, 0x01, sizeof(curr_game->level));
                curr_game->x_pos = starting_x;
                curr_game->y_pos = starting_y;
                printf("Made it past intS!\n");
                strcpy(curr_game->player_name, recv_packet->data);
                printf("Made it past string copy!\n");
                printf("PLAYER X POS : %d\n", curr_game->x_pos);
                printf("PLAYER Y POS : %d\n", curr_game->y_pos);
                printf("PLAYER NAME : %s \n", curr_game->player_name);

                printf("above packet response\n");
                resp_packet = create_packet(RESP_REGISTERED, strlen(register_success) + 1, register_success);
                printf("RESP TYPE : %d\n", resp_packet->type);
                printf("RESP LEN : %d\n", resp_packet->length);
                printf("RESP DATA : %s\n", resp_packet->data);
                printf("Below packet response\n");
                if (NULL == resp_packet)
                {
                    perror("failed to create response packet!\n");
                    break;
                }
                printf("Made it to serialize packet\n");
                if (serialize_packet(resp_packet, resp_buff))
                {
                    printf("In serialize packet\n");
                    bytes_sent = send(connfd, resp_buff, strlen(resp_buff) - 1, 0);

                    if (-1 == bytes_sent)
                    {
                        perror("Failed to send data to client!\n");
                        break;
                    }
                }
                printf("Successfully Responded to the client\n");
                connected = 1;
                free(recv_packet->data);
                recv_packet-> data = NULL;
                free(recv_packet);
                recv_packet = NULL;
                free(resp_packet->data);
                resp_packet-> data = NULL;
                free(resp_packet);
                resp_packet = NULL;
                break;
            
            case REQ_GET_LEVEL:
                printf("START OF GETTING DISPLAY!!!\n\n");
                if (0 == connected)
                {
                    break;
                }
                recv_packet = deserialize_packet(buff, bytes_received);

                if (NULL == recv_packet)
                {
                    perror("Failed to deserialize packet!\n");
                    break;
                }
                printf("RECV TYPE : %d\n", recv_packet->type);
                printf("RECV LEN : %d\n", recv_packet->length);

                printf("CURR GAME NAME : %s\n", curr_game->player_name);
                uint8_t * serialized_level = serialize_game_data(curr_game);

                if (NULL == serialized_level)
                {
                    perror("Err : Calloc Failure\n");
                    break;
                }
                
                printf("CURR LEVEL: %s\n", serialized_level);

                printf("above packet response\n");
                resp_packet = create_packet(RESP_LEVEL, strlen(serialized_level) + 1, serialized_level);
                printf("RESP TYPE : %d\n", resp_packet->type);
                printf("RESP LEN : %d\n", resp_packet->length);
                printf("RESP DATA : %s\n", resp_packet->data);
                printf("Below packet response\n");
                if (NULL == resp_packet)
                {
                    perror("failed to create response packet!\n");
                    break;
                }
                printf("Made it to serialize packet\n");
                if (serialize_packet(resp_packet, resp_buff))
                {
                    for (int i = 0; i < resp_packet->length; i++)
                    {
                        printf("%02x", resp_buff[i]);
                    }
                    printf("In serialize packet\n");
                    bytes_sent = send(connfd, resp_buff, resp_packet->length + 2, 0);

                    if (-1 == bytes_sent)
                    {
                        perror("Failed to send data to client!\n");
                        break;
                    }
                    break;
                }
                printf("Successfully Responded to the client\n");
                break;

            case REQ_NEW_GAME:
                break;
            
            case REQ_SAVE_GAME:
            
                break;
            
            case REQ_LOAD_GAME:

                break;
            
            case REQ_MOVE:
                break;
        }

    }
}



int main (int argc, char const * argv[])
{

    int sockfd = 0;
    int connfd = 0;
    int len = 0;
    int running = 1;
    int optval = 1;
    struct sockaddr_in servaddr = {0};
    struct sockaddr_in cliaddr = {0};

    sockfd = socket(AF_INET, SOCK_STREAM, 0);

    if (-1 == sockfd)
    {
        printf("Socket Creation Failed \n");
        exit(0);
    }  
    
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &optval, sizeof(optval)) < 0)
    {
        printf("Set Sock Opt Failed \n");
    }
    printf("Socket Successfully Connected!\n");

    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    servaddr.sin_port = htons(PORT);

    if ((0 != bind(sockfd, (struct sockaddr *) &servaddr, sizeof(servaddr))))
    {
        printf("Socket Binding Failed!\n");
    }

    printf("Socket Successfully Binded!\n");

    if ((0 != listen(sockfd, 5)))
    {
        printf("Err : Listen Failure\n");
        exit(0);
    }

    printf("Server listening \n");

    len = sizeof(cliaddr);

    connfd = accept(sockfd, (struct sockaddr *) &cliaddr, &len);

    if (0 > connfd)
    {
        printf("Server accept failed\n");
        exit(0);
    }

    printf("Client Has Been Accepted! \n");

    game_loop(connfd, running);

    close(sockfd);
}