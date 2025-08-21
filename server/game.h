#ifndef GAME_H
#define GAME_H

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

typedef struct
{
    uint8_t x_pos;
    uint8_t y_pos;
    uint8_t level[10][10];
    uint8_t health;
    char current_items[100];
    char player_name[128];

} game_t;

typedef enum
{
    DEFAULT = 1,
    PLAYER,
    ENEMY,
    OBSTACLE,
    OBSTACLE_HIT,
    ENEMY_HIT,
    EXIT,

} game_constraints_e;

/**
 * @brief 
 * validates move and updates game state
 * @param game 
 * @return true 
 * @return false 
 */
bool make_move(game_t * game, char * move);

/**
 * @brief 
 * checks the state for a win or lore condition
 * @param game 
 * @return true 
 * @return false 
 */
int check_state(game_t * game);

/**
 * @brief 
 * poopulates the game with AI players
 * @param game 
 * @return true 
 * @return false 
 */
bool populate_ai(game_t * game);

/**
 * @brief 
 * randomizes the AI players
 * @param game 
 * @return true 
 * @return false 
 */
int randomize_ai(game_t * game);

/**
 * @brief 
 * randomizes the choices for the player
 * @param game 
 * @return true 
 * @return false 
 */
bool randomize_choices (game_t * game);

/**
 * @brief 
 * 
 * @param game 
 * @return true 
 * @return false 
 */
bool save_game(game_t * game);

/**
 * @brief 
 * 
 * @param game 
 * @return true 
 * @return false 
 */
game_t * load_game(game_t * game);

/**
 * @brief 
 * serialize the game data into a byte array to send to the client
 * @param game 
 * @return true 
 * @return false 
 */
uint8_t * serialize_game_data(game_t * game);

#endif