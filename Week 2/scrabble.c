#include <ctype.h>
#include <cs50.h>
#include <stdio.h>
#include <string.h>

int calculate_score(string s);

string letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
int scores[26] = {1, 3, 3, 2, 1, 4, 2, 4, 1, 8, 5, 1, 3, 1, 1, 3, 10, 1, 1, 1, 1, 4, 4, 8, 4, 10};

int main(void)
{
    string player_one = get_string("Player 1: ");
    string player_two = get_string("Player 2: ");

    int p1_score = calculate_score(player_one);
    int p2_score = calculate_score(player_two);

    //printf("Player one scored %i\nPlayer two scored %i\n", p1_score, p2_score);

    if(p1_score > p2_score){
        printf("Player 1 wins!\n");
    } else if(p2_score > p1_score){
        printf("Player 2 wins!\n");
    } else {
        printf("Tie!\n");
    }
}

int calculate_score(string s)
{
    int cscore = 0;
    for(int i = 0; i < strlen(s); i++)
    {
        if(isalpha(s[i]))
        {
            //printf("%c is a letter\n", player_one[i]);
            for(int j = 0; j < strlen(letters); j++)
            {
                if(letters[j] == toupper(s[i]))
                {
                    //printf("%c = %c\n", letters[j], player_one[i]);
                    cscore += scores[j];
                } else {
                    continue;
                }
            }
        } else {
            //printf("%c is not a letter\n", player_one[i]);
            continue;
        }
    }
    return cscore;
}
