#include "game.h"

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>

#define ROWS 10
#define COLS 10

bool make_move(game_t * game, char * move)
{
    int dx = 0;
    int dy = 0;
    int x = 0;
    int y = 0;
    int new_x = 0;
    int new_y = 0;
    int target = 0;

    if (0 == strcmp(move, "up"))
    {
        dy = -1;
    }
    else if (0 == strcmp(move, "down"))
    {
        dy = 1;
    }
    else if (0 == strcmp(move, "left"))
    {
        dx = -1;
    }
    else if (0 == strcmp(move, "right"))
    {
        dx = 1;
    }
    else
    {
        return false;
    }

    x = game->x_pos;
    y = game->y_pos;
    new_x = x + dx;
    new_y = y + dy;
    
    //Check if they are in bounds
    if ((0 > new_x) || (COLS <= new_x) || (0 > new_y) || (ROWS <= new_y))
    {
        return false;
    }

    target = game->level[new_y][new_x];

    if (OBSTACLE == target)
    {
        game->level[new_y][new_x] = OBSTACLE_HIT;
        game->x_pos = new_x;
        game->y_pos = new_y;
        return true;
    }
    else if (ENEMY == target)
    {
        game->level[new_y][new_x] = ENEMY_HIT;
        game->x_pos = new_x;
        game->y_pos = new_y;
        return true;
    }
    else
    {
        // Move Player
        game->level[y][x] = 0;
        game->level[new_y][new_x] = PLAYER;
        game->x_pos = new_x;
        game->y_pos = new_y;
        return true;
    }
}

// 0 equals no issue 1 equals obstacle hit 2 equals enemy hit 3 equals error
int check_state(game_t * game)
{   
    if (game->level[game->y_pos][game->x_pos] == PLAYER)
    {
        return 0;
    }
    else if (game->level[game->y_pos][game->x_pos] == OBSTACLE_HIT)
    {
        return 1;
    }
    else if (game->level[game->y_pos][game->x_pos] == ENEMY_HIT)
    {
        return 2;
    }

    return 3;
}


bool populate_board(game_t * game)
{
    int min = 0;
    int max = 9;
    srand(time(NULL));
    int ai_placed = 0;
    int random_number = 0;
    int random_number2 = 0;

    while (10 != ai_placed)
    {
        random_number = (rand() % (10 - 1 + 1)) + min;
        random_number2 = (rand() % (10 - 1 + 1)) + min;

        if (random_number == 9 && random_number2 == 4)
        {
            continue;
        }
        game->level[random_number][random_number2] = ENEMY;
        ai_placed++;
    }
    
    game->level[9][4] = PLAYER;

    return true;
}

bool populate_obstacles(game_t *game)
{
    int min = 0;
    int max = 9;
    srand(time(NULL));
    int obstacles_placed = 0;
    int random_number = 0;
    int random_number2 = 0;

    while (10 != obstacles_placed)
    {
        random_number = (rand() % (max - min + 1)) + min;
        random_number2 = (rand() % (max - min + 1)) + min;

        if (random_number == 9 && random_number2 == 4)
        {
            continue;
        }
        game->level[random_number][random_number2];
        obstacles_placed++;
    }

    return true;
}

// damage randomized from 10 to 100 
int randomize_ai(game_t * game)
{
    srand(time(NULL));

    int min_damage = 10;
    int max_damage = 100;
    int damage_done = 0;

    damage_done = (rand() % (max_damage - min_damage + 1)) + min_damage;

    return damage_done;
}

bool randomize_choices (game_t * game)
{
    
    return false;
}

bool save_game(game_t * game)
{
    return false;
}


game_t * load_game(game_t * game)
{
    return NULL;
}

uint8_t * serialize_game_data(game_t * game)
{
    uint8_t * buffer = NULL;
    uint8_t offset = 0;

    game->level[9][4] = PLAYER;
    buffer = calloc(102, sizeof(uint8_t));

    printf("Size of game_t %ld\n", sizeof(*game));

    if (NULL == buffer)
    {
        perror("Calloc Failure!\n");
        return NULL;
    }

    memcpy(buffer, game->level, sizeof(game->level));
    offset += sizeof(game->level);
    buffer[offset] = game->health;
    offset += sizeof(uint8_t);
    buffer[offset] = '\0';
    printf("THIS WORKED!\n");
    return buffer;
    // need to eventually add items here
}
