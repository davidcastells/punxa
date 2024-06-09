// 17/12/2013
// This encoder implemented by David Castells-Rufas (david.castells@uab.cat)
// to do research in parallel implementation of the JPEG encoding algorithm
// The code is implemented in C++ and derived from a Java version
//
// The application contains code from (at least) the following authors
//      James R. Weeks (James@obrador.com)
//      Florian Raemy
//      Benjamin Kalytta
//      Vladimir Antonenko
//      Thomas G. Lane
//
#include "JpegEncoder.h"
#include "Bitmap.h"
#include "SmallEmbeddedImage.h"
#include "FileOutputStream.h"
#include "ByteArrayOutputStream.h"
#include "globals.h"

#include "PerformanceCounter.h"

#include <stdio.h>

void usage()
{
    printf("Usage: jpegenc_seq [OPTIONS]...\n");
    printf("\nEncodes a bitmap into JPEG\n");
    printf("\nOptions:\n");
    printf("  -i\tInput Bitmap (.BMP) File\n");
    printf("  -o\tOutput Bitmap (.JPG) File\n");
    printf("  -m\tUse embedded static input image\n");
    printf("  -n\tWrite output to internal static array\n");
    printf("  -v\tVerbose output\n");
    printf("  -t\tMeasure time\n");
    printf("  -p\tMeasure power\n");
    printf("\n");
}

char* inputFile = NULL;
char* outputFile = NULL;
int verbose = 0;

int staticInputImage = 0;
int staticOutputStream = 0;
int reportTime = 0;
int testPower = 0;

/**
 * Parse parameters
 * @param argc
 * @param args
 * @return 1 if any error occurred
 */
int parseArguments(int argc, char* args[])
{
    for (int i=0; i < argc; i++)
    {
        if (strcmp(args[i], "-i") == 0)
        {
            staticInputImage = 0;
            inputFile = args[++i];
        }
        else if (strcmp(args[i], "-o") == 0)
        {
            outputFile = args[++i];
        }         
        else if (strcmp(args[i], "-v") == 0)
        {
            verbose = 1;
        }
        else if (strcmp(args[i], "-m") == 0)
        {
            staticInputImage = 1;
        }
        else if (strcmp(args[i], "-n") == 0)
        {
            staticOutputStream = 1;
        }
        else if (strcmp(args[i], "-t") == 0)
        {
            reportTime = 1;
        }
        else if (strcmp(args[i], "-p") == 0)
        {
            testPower = 1;
        }
    }
    
    if (inputFile == NULL && staticInputImage == 0)
    {
        printf("ERROR: No intput File\n");
        return 1;
    }
    
    if (outputFile == NULL && staticOutputStream == 0)
    {
        printf("ERROR: No output file\n");
        return 1;
    }
    
    return 0;
}

/**
 *  The application assumes that there is a test.bmp image in the current directory
 *  and creates a resulting test.jpg with the encoded file
 */
int main(int argc, char* args[])
{	
	printf("Jpeg Encoder Test " __TIMESTAMP__ "\n");
	
        if (parseArguments(argc, args))
        {
            usage();
            exit(-1);
        }
        
        Image* inputImage = NULL;
        OutputStream* outputStream = NULL;
        
        if (staticInputImage)
        {
            // 
            inputImage = new EmbeddedImage();
	    printf("using embedded input image %d x %d\n", inputImage->getWidth(), inputImage->getHeight());
        }
        else
        {
            CBitmap* bitmap = new CBitmap();

            if (bitmap->load(inputFile))
                    printf("Loaded %s\n", inputFile);
            else
            {
                    printf("Failed to load %s\n", inputFile);
                    exit(1);
            }
            
            inputImage = bitmap;
	}
        
        
        
	
        
        while (1)
        {
            uint64 t0, tf;
            
            if (staticOutputStream)
            {
                ByteArrayOutputStream* bos = new ByteArrayOutputStream(46000);   // file is 44KB
                outputStream = bos;
            }
            else
            {
                FileOutputStream* fos = new FileOutputStream(outputFile);
                outputStream = fos;
		printf("creating output stream %s\n", outputFile);
            }


            JpegEncoder encoder(inputImage, 80, outputStream);
            
            if (reportTime) perfCounter(&t0);
            encoder.Compress();
            if (reportTime) perfCounter(&tf);
            double r, fps;

	printf("done!\n");

		if (reportTime)
		{
			r = secondsBetweenLaps(t0, tf);
             fps = 1/r;

                printf("Time to compress JPEG image: %.5f s (%.2f FPS)\n", r, fps);
           }
 
            outputStream->close();

	printf("output stream closed\n");
            delete outputStream;
            
            if (!testPower)
                return 0;
        }
        
	return 0;
	
}
