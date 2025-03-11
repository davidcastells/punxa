#include <stdio.h>


typedef unsigned long long uint64_t;

int hamming(uint64_t a, uint64_t b) 
{
    uint64_t xor_result = a ^ b; // XOR to find differing bits
    int distance = 0;
    while (xor_result) {
        distance += xor_result & 1; // Count set bits
        xor_result >>= 1;
    }
    return distance;
}

static inline __attribute__((always_inline)) unsigned long hamming_ci(unsigned long rs1, unsigned long rs2) 
{
    unsigned long rd;

    asm volatile (".insn r 0x0b, 0, 0, %0, %1, %2" : "=r" (rd) : "r" (rs1), "r" (rs2)); 
        
    return rd;
}


int hamming_vector(uint64_t* a, uint64_t* b, int len)
{
    int r = 0, i;
    for (i=0; i < len; i++)
    {
    #ifdef USE_CI
        r += hamming_ci(a[i], b[i]);
    #else
        r += hamming(a[i], b[i]);
    #endif
    }
        
    return r;        
}

int main(int argc, char* args[])
{
    uint64_t a[20] = {
        0x3A7D9F2B4C6E1A8D, 0x5E8B3F6A9D2C4F1E, 0x1F4A6B8C3D5E7F29, 0x6B8C3D5E7F291F4A,
        0x8C3D5E7F291F4A6B, 0x3D5E7F291F4A6B8C, 0x5E7F291F4A6B8C3D, 0x7F291F4A6B8C3D5E,
        0x291F4A6B8C3D5E7F, 0x1F4A6B8C3D5E7F29, 0x4A6B8C3D5E7F291F, 0x6B8C3D5E7F291F4A,
        0x8C3D5E7F291F4A6B, 0x3D5E7F291F4A6B8C, 0x5E7F291F4A6B8C3D, 0x7F291F4A6B8C3D5E,
        0x291F4A6B8C3D5E7F, 0x1F4A6B8C3D5E7F29, 0x4A6B8C3D5E7F291F, 0x6B8C3D5E7F291F4A
    };

    uint64_t b[20] = {
        0x5E8B3F6A9D2C4F1E, 0x1F4A6B8C3D5E7F29, 0x6B8C3D5E7F291F4A, 0x8C3D5E7F291F4A6B,
        0x3D5E7F291F4A6B8C, 0x5E7F291F4A6B8C3D, 0x7F291F4A6B8C3D5E, 0x291F4A6B8C3D5E7F,
        0x1F4A6B8C3D5E7F29, 0x4A6B8C3D5E7F291F, 0x6B8C3D5E7F291F4A, 0x8C3D5E7F291F4A6B,
        0x3D5E7F291F4A6B8C, 0x5E7F291F4A6B8C3D, 0x7F291F4A6B8C3D5E, 0x291F4A6B8C3D5E7F,
        0x1F4A6B8C3D5E7F29, 0x4A6B8C3D5E7F291F, 0x6B8C3D5E7F291F4A, 0x8C3D5E7F291F4A6B
    };

    uint64_t c[20] = {
        0x1F4A6B8C3D5E7F29, 0x6B8C3D5E7F291F4A, 0x8C3D5E7F291F4A6B, 0x3D5E7F291F4A6B8C,
        0x5E7F291F4A6B8C3D, 0x7F291F4A6B8C3D5E, 0x291F4A6B8C3D5E7F, 0x1F4A6B8C3D5E7F29,
        0x4A6B8C3D5E7F291F, 0x6B8C3D5E7F291F4A, 0x8C3D5E7F291F4A6B, 0x3D5E7F291F4A6B8C,
        0x5E7F291F4A6B8C3D, 0x7F291F4A6B8C3D5E, 0x291F4A6B8C3D5E7F, 0x1F4A6B8C3D5E7F29,
        0x4A6B8C3D5E7F291F, 0x6B8C3D5E7F291F4A, 0x8C3D5E7F291F4A6B, 0x3D5E7F291F4A6B8C
    };

    // Initialize distance matrix
    uint64_t* in[3] = {a,b,c};
    int distance_matrix[3][3] = {0};
    int x,y;
    // Compute the distance matrix
    for (y=0; y < 3; y++)
        for (x=0; x < 3; x++)
            distance_matrix[x][y] = hamming_vector(in[x], in[y], 20);

    // Print the distance matrix
    printf("Distance Matrix:\n");
    printf("       a      b      c\n");
    printf("a: %6d %6d %6d\n", distance_matrix[0][0], distance_matrix[0][1], distance_matrix[0][2]);
    printf("b: %6d %6d %6d\n", distance_matrix[1][0], distance_matrix[1][1], distance_matrix[1][2]);
    printf("c: %6d %6d %6d\n", distance_matrix[2][0], distance_matrix[2][1], distance_matrix[2][2]);

    return 0;
}
