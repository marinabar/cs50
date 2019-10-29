#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>

int check_key(string argv);
int encode_key(char c);

int main(int argc, string argv[])
{
    if (argc != 2 || check_key(argv[1]) != 0)
    {
        printf("Usage: ./vigenere keyword\n");
        return 1;
    }

    else
    {
        int key;
        int y = -1;
        int ciphertext;
        //get plaintext
        string plaintext = get_string("plaintext: ");
        printf("ciphertext: ");

        //iterate
        for (int j = 0, l = strlen(plaintext); j < l; j++)
        {
            if (isalpha(plaintext[j]))
            {
                y++;
                key = encode_key(tolower(argv[1][y % strlen(argv[1])]));
                ciphertext = (int) plaintext[j] + key;
                if ((int) tolower(plaintext[j]) + key > 122)
                {
                    ciphertext = ciphertext - 26;
                    printf("%c", (char) ciphertext);
                }
                else
                {
                    printf("%c", (char) ciphertext);
                }
            }
            else
            {
                printf("%c", (char) plaintext[j]);
            }
        }
        printf("\n");
    }
}




int encode_key(char c)
{
    int key = (int) c - 97;
    return key;
}

//check if it's valid
int check_key (string argv)
{
    for (int i = 0, n = strlen(argv); i < n; i++)
    {
        if (!isalpha(argv[i]))
        {
            return 1;
        }
    }

    return 0;
}
