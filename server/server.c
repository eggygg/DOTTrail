#include "server.h"
#include "game.h"

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>



server_t * deserialize_packet(uint8_t * buffer, size_t length)
{
    server_t * recv_info = calloc(1, sizeof(server_t));
    
    if (NULL == recv_info)
    {
        perror("Calloc Failure\n");
        return NULL;
    }

    recv_info->type = buffer[0];
    recv_info->length = buffer[1];

    recv_info->data = calloc(recv_info->length + 1, sizeof(char));
    
    if (NULL == recv_info->data)
    {
        perror("Calloc Failure\n");
        return NULL;
    }

    memcpy(recv_info->data, buffer + 2, recv_info->length + 1);

    recv_info->data[recv_info->length] = '\0';

    return recv_info;
}


server_t * create_packet(uint8_t type, size_t len, char data[])
{
    server_t * resp_msg = calloc(1, sizeof(server_t));

    if (NULL == resp_msg)
    {
        perror("Failure to allocate for response message\n");
        return NULL;
    }

    resp_msg->type = type;
    resp_msg->length = len;

    resp_msg->data = calloc(len, sizeof(char));
    if (NULL == resp_msg->data)
    {
        perror("Failure to allocate for response message\n");
        return NULL;
    }

    memcpy(resp_msg->data, data, len);

    return resp_msg;
}


bool serialize_packet(server_t * packet, uint8_t buffer[])
{
    buffer[0] = packet->type;
    buffer[1] = packet->length;
    packet->data = packet->data;
    memcpy(buffer + 2, packet->data, packet->length);
    return true;
}


void free_message(server_t * msg)
{

    if (msg)
    {
        free(msg->data);
        free(msg);
    }
    msg->data = NULL;
    msg = NULL;
    return;
}