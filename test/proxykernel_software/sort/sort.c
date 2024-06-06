#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINES 1000
#define MAX_LINE_LENGTH 256

// Function to compare two strings for qsort
int compare_strings(const void *a, const void *b) {
    return strcmp(*(const char **)a, *(const char **)b);
}

int main() {
    FILE *inputFile, *outputFile;
    char *lines[MAX_LINES];
    char buffer[MAX_LINE_LENGTH];
    int lineCount = 0;

    // Open the input file
    inputFile = fopen("input.txt", "r");
    if (inputFile == NULL) {
        perror("Error opening input file");
        return EXIT_FAILURE;
    }

    // Read lines from the input file
    while (fgets(buffer, sizeof(buffer), inputFile)) {
        if (lineCount >= MAX_LINES) {
            fprintf(stderr, "Too many lines in input file\n");
            return EXIT_FAILURE;
        }
        lines[lineCount] = strdup(buffer);
        if (lines[lineCount] == NULL) {
            perror("Error allocating memory");
            return EXIT_FAILURE;
        }
        lineCount++;
    }
    fclose(inputFile);

    // Sort the lines
    qsort(lines, lineCount, sizeof(char *), compare_strings);

    // Open the output file
    outputFile = fopen("output.txt", "w");
    if (outputFile == NULL) {
        perror("Error opening output file");
        return EXIT_FAILURE;
    }

    // Write sorted lines to the output file
    for (int i = 0; i < lineCount; i++) {
        fputs(lines[i], outputFile);
        free(lines[i]); // Free the allocated memory for each line
    }
    fclose(outputFile);

    printf("Lines sorted and written to output.txt\n");
    return EXIT_SUCCESS;
}

