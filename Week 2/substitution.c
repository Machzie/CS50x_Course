#include <ctype.h>
#include <cs50.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int check_valid_key(string k);
int checkalpha(string s);
int checkunique(string s);

int main(int argc, string argv[])
{
    if(argc != 2)
    {
        printf("Usage: ./substitution key\n");
        return 1;
    }
    else
    {
        string key = argv[1];
        if(check_valid_key(key) == 0)
        {
            string plain_text = get_string("plaintext: ");
            //printf("The key is %s\n", key);
            //printf("The text is %s\n", plain_text);

            int offset[26];
            int key_int[26];
            for(int i = 0; i < 26; i++)
            {
                key_int[i] = toupper(key[i]);
                offset[i] = (65+i) - key_int[i];
                //printf("Offset is %i\n", offset[i]);
            }

            int cipher_int[strlen(plain_text)];
            char cipher_char[strlen(plain_text)];
            for(int j = 0; j < strlen(plain_text); j++)
            {
                if(plain_text[j] >= 65 && plain_text[j] <= 90)
                {
                    cipher_int[j] = plain_text[j] - offset[plain_text[j]-65];
                    cipher_char[j] = cipher_int[j];
                    //printf("Cipher int is %c\n", cipher_int[j]);
                }
                else if(plain_text[j] >= 97 && plain_text[j] <= 122)
                {
                    cipher_int[j] = plain_text[j] - offset[plain_text[j]-97];
                    cipher_char[j] = cipher_int[j];
                }
                else
                {
                    cipher_int[j] = plain_text[j];
                    cipher_char[j] = cipher_int[j];
                    printf("Cipher int %i\n", cipher_int[j]);
                }
            }
            cipher_char[strlen(plain_text)] = '\0';
            printf("ciphertext: %s\n", cipher_char);
        }
        else
        {
            return 1;
        }
    }
}

int check_valid_key(string k)
{
    if(strlen(k) != 26)
    {
        printf("Key must contain 26 characters\n");
        return 2;
    }
    else
    {
        if(checkalpha(k) != 0)
        {
            printf("The key must contain only letter characters\n");
            return 3;
        }
        else if(checkunique(k) != 0)
        {
            printf("The key must contain unique characters\n");
            return 4;
        }
        {
        return 0;
        }
    }
}

int checkalpha(string s)
{
    for (int i = 0; i < strlen(s); i++)
    {
        if (isalpha(s[i]))
        {
            continue;
        }
        else
        {
            return 1;
        }
    }
    return 0;
}

int checkunique(string s)
{
    int a[90] = {0}; // Initiate an empty array of 90 characters
    for(int i = 0; i < strlen(s); i++)
    {
        int ascii_num = toupper(s[i]); // Convert to upper just for comparison
        if(a[ascii_num] == 1)
        {
            return 1;
        }
        else
        {
            a[ascii_num] = 1;
        }
    }
    return 0;
}
