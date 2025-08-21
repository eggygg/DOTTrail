// #ifndef SERVER_H
// #define SERVER_H

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

typedef enum
{
    REQ_REGISTER = 1,
    REQ_NEW_GAME,
    REQ_SAVE_GAME,
    REQ_LOAD_GAME,
    REQ_MOVE,
    REQ_GET_LEVEL,
    RESP_STANDARD = 64,
    RESP_REGISTERED,
    RESP_LEVEL,
    RESP_WIN,
    RESP_LOSE,
    RESP_ERROR
} message_type_e;


typedef struct
{
    uint8_t type;
    uint8_t length;
    uint8_t * data;
} server_t;



/**
 * @brief 
 * 
 * @param buffer 
 * @param length 
 * @return server_t* 
 */
server_t * deserialize_packet(uint8_t * buffer, size_t length);

/**
 * @brief Create a packet object
 * 
 * @param type 
 * @param data 
 * @return server_t* 
 */
server_t * create_packet(uint8_t type, size_t len, char * data);

/**
 * @brief 
 * 
 * @param packet 
 * @param buffer 
 * @return true 
 * @return false 
 */
bool serialize_packet(server_t * packet, uint8_t * buffer);

/**
 * @brief 
 * 
 * @param msg 
 */
void free_message(server_t * msg);




// #endif