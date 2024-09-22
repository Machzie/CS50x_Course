#include <ctype.h>
#include <cs50.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

float calc_index(int num_letters, int num_sentences, float num_words);
float number_of_words(string s);
int number_of_letters(string s);
int number_of_sentences(string s);

int main(void)
{
    string text = get_string("Enter the text: ");
    int numw = number_of_words(text);
    int numl = number_of_letters(text);
    int nums = number_of_sentences(text);
    printf("Number of words: %i\n", numw);
    printf("Number of letters: %i\n", numl);
    printf("Number of sentences: %i\n", nums);
    int grade = round(calc_index(numl, nums, numw));
    if (grade < 1)
    {
        printf("Before Grade 1\n");
    }
    else if (grade > 16)
    {
        printf("Grade 16+\n");
    }
    else
    {
        printf("Grade %i\n", grade);
    }
}

float calc_index(int num_letters, int num_sentences, float num_words)
{
    float l = (num_letters*100) / num_words; // number of letters per 100 words
    float s = (num_sentences*100) / num_words; // number of letters per 100 words
    printf("There are %f letters per 100 words\n", l);
    printf("There are %f sentences per 100 words\n", s);
    float index = 0.0588 * l - 0.296 * s - 15.8;
    printf("Index = %f\n", index);
    return index;
}

float number_of_words(string s)
{
    int word_count = 1;
    for (int i = 0; i < strlen(s); i++)
    {
        if (s[i] == ' ')
        {
            word_count++;
        }
    }
    return word_count;
}

int number_of_letters(string s)
{
    int letter_count = 0;
    for (int i = 0; i < strlen(s); i++)
    {
        if (isalpha(s[i]))
        {
            letter_count++;
        }
    }
    return letter_count;
}

int number_of_sentences(string s)
{
    int sentence_count = 0;
    for (int i = 0; i < strlen(s); i++)
    {
        if (s[i] == '!' || s[i] == '.' || s[i] == '?')
        {
            sentence_count++;
        }
    }
    return sentence_count;
}
