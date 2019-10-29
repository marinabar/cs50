#include <stdio.h>
#include <cs50.h>

int main(void)
{
    long long card_num;

    do
    {
        card_num = get_long("Number: ");
    }

    while (card_num < 1 || card_num > 9999999999999999);

    long long card_num2 = card_num;

    int c = 0;

    while (card_num2 > 0)
    {
        card_num2 = card_num2 / 10;
        c++;
    }


    if (c != 13 && c != 15 && c != 16)
    {
        printf("INVALID\n");
    }


    card_num2 = card_num;

    while (card_num2 > 100)
    {
        card_num2 = card_num2 / 10;
    }

    int card_type = card_num2;


    if (card_type > 50 && card_type < 56 && c == 16)
    {
        printf("MASTERCARD\n") ;
    }
    else if ((card_type == 34 || card_type == 37) && (c == 15)) 
    {
        printf("AMEX\n") ;
    }
    else if ((card_type / 10 == 4) && (c == 13 || c == 16 || c == 19))
    {
        printf("VISA\n") ;
    }
    else
    {
        printf("INVALID\n");
    }

    int s = 0;

    card_num2 = card_num;

    for (int i = 1; i <= c; i++)
    {
        int fd = card_num2 % 10;

        if (i % 2 == 0)
        {
            fd *= 2;

            if (fd > 9)
            {
                fd -= 9;
            }
        }

        s += fd;

        card_num2 /= 10;
    }

    if (s % 10 != 0)
    {
        printf("INVALID\n");
    }

} 
