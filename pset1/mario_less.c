#include <cs50.h>
#include <stdio.h>

int main(void)
{
    int height;
    do
    {
        height = get_int("Height: ");
    }
    while (height <= 0 || height >= 9);
    for (int i = 1; i <= height; i++)
            {
                for (int y = height - i; y > 0; y--)
                {
                    printf(" ");
                }
                for (int x = 1; x <= i; x++)
                {
                    printf("#");
                }
            printf("\n");
            }
}
