// 17/12/2013
// This encoder implemented by David Castells-Rufas (david.castells@uab.cat)
// to do research in parallel implementation of the JPEG encoding algorithm
// The code is implemented in C++ and derived from a Java version, see previous
// author licences below
//

#include "DCT.h"

#include "globals.h"

#include <math.h>
#include <stdio.h>

#define PI 3.14159265359

// This class incorporates quality scaling as implemented in the JPEG-6a
// library.

 /*
 * DCT - A Java implementation of the Discreet Cosine Transform
 */




    /**
     * Constructs a new DCT object. Initializes the cosine transform matrix
     * these are used when computing the DCT and it's inverse. This also
     * initializes the run length counters and the ZigZag sequence. Note that
     * the image quality can be worse than 25 however the image will be
     * extemely pixelated, usually to a block size of N.
     *
     * @param QUALITY The quality of the image (0 worst - 100 best)
     *
     */
     DCT::DCT()
    { 
    	   // Image Quality (0-100) - default 80 (good image / good compression)
    	   QUALITY = 80;
    
    	   quantum_luminance = &quantum[0][0];
    	   quantum_chrominance = &quantum[1][0];

    	    DivisorsLuminance = &Divisors[0][0];
    	    DivisorsChrominance = &Divisors[1][0];

    }
    
    void DCT::init(int QUALITY)
    {
        initMatrix(QUALITY);
    }


    /*
     * This method sets up the quantization matrix for luminance and
     * chrominance using the Quality parameter.
     */
    void DCT::initMatrix(int quality)
    {
        
        BIGFP AANscaleFactor[] = { 1.0, 1.387039845, 1.306562965, 1.175875602,
                                    1.0, 0.785694958, 0.541196100, 0.275899379};
        int i;
        int j;
        int index;
        int Quality;
        int temp;

        if (verbose)
            printf("Initializing DCT with quality %d\n", quality);
        
        
// converting quality setting to that specified in the jpeg_quality_scaling
// method in the IJG Jpeg-6a C libraries

        Quality = quality;
        if (Quality <= 0)
                Quality = 1;
        if (Quality > 100)
                Quality = 100;
        if (Quality < 50)
                Quality = 5000 / Quality;
        else
                Quality = 200 - Quality * 2;

// Creating the luminance matrix

        quantum_luminance[0]=16;
        quantum_luminance[1]=11;
        quantum_luminance[2]=10;
        quantum_luminance[3]=16;
        quantum_luminance[4]=24;
        quantum_luminance[5]=40;
        quantum_luminance[6]=51;
        quantum_luminance[7]=61;
        quantum_luminance[8]=12;
        quantum_luminance[9]=12;
        quantum_luminance[10]=14;
        quantum_luminance[11]=19;
        quantum_luminance[12]=26;
        quantum_luminance[13]=58;
        quantum_luminance[14]=60;
        quantum_luminance[15]=55;
        quantum_luminance[16]=14;
        quantum_luminance[17]=13;
        quantum_luminance[18]=16;
        quantum_luminance[19]=24;
        quantum_luminance[20]=40;
        quantum_luminance[21]=57;
        quantum_luminance[22]=69;
        quantum_luminance[23]=56;
        quantum_luminance[24]=14;
        quantum_luminance[25]=17;
        quantum_luminance[26]=22;
        quantum_luminance[27]=29;
        quantum_luminance[28]=51;
        quantum_luminance[29]=87;
        quantum_luminance[30]=80;
        quantum_luminance[31]=62;
        quantum_luminance[32]=18;
        quantum_luminance[33]=22;
        quantum_luminance[34]=37;
        quantum_luminance[35]=56;
        quantum_luminance[36]=68;
        quantum_luminance[37]=109;
        quantum_luminance[38]=103;
        quantum_luminance[39]=77;
        quantum_luminance[40]=24;
        quantum_luminance[41]=35;
        quantum_luminance[42]=55;
        quantum_luminance[43]=64;
        quantum_luminance[44]=81;
        quantum_luminance[45]=104;
        quantum_luminance[46]=113;
        quantum_luminance[47]=92;
        quantum_luminance[48]=49;
        quantum_luminance[49]=64;
        quantum_luminance[50]=78;
        quantum_luminance[51]=87;
        quantum_luminance[52]=103;
        quantum_luminance[53]=121;
        quantum_luminance[54]=120;
        quantum_luminance[55]=101;
        quantum_luminance[56]=72;
        quantum_luminance[57]=92;
        quantum_luminance[58]=95;
        quantum_luminance[59]=98;
        quantum_luminance[60]=112;
        quantum_luminance[61]=100;
        quantum_luminance[62]=103;
        quantum_luminance[63]=99;

        for (j = 0; j < 64; j++)
        {
                temp = (quantum_luminance[j] * Quality + 50) / 100;
                if ( temp <= 0) temp = 1;
                if (temp > 255) temp = 255;
                quantum_luminance[j] = temp;
        }
        index = 0;
        for (i = 0; i < 8; i++) {
                for (j = 0; j < 8; j++) {
// The divisors for the LL&M method (the slow integer method used in
// jpeg 6a library).  This method is currently (04/04/98) incompletely
// implemented.
//                        DivisorsLuminance[index] = ((double) quantum_luminance[index]) << 3;
// The divisors for the AAN method (the float method used in jpeg 6a library.
                        DivisorsLuminance[index] = (BIGFP) ((BIGFP)1.0/((BIGFP) quantum_luminance[index] * AANscaleFactor[i] * AANscaleFactor[j] * (BIGFP) 8.0));
                        index++;
                }
        }


// Creating the chrominance matrix

        quantum_chrominance[0]=17;
        quantum_chrominance[1]=18;
        quantum_chrominance[2]=24;
        quantum_chrominance[3]=47;
        quantum_chrominance[4]=99;
        quantum_chrominance[5]=99;
        quantum_chrominance[6]=99;
        quantum_chrominance[7]=99;
        quantum_chrominance[8]=18;
        quantum_chrominance[9]=21;
        quantum_chrominance[10]=26;
        quantum_chrominance[11]=66;
        quantum_chrominance[12]=99;
        quantum_chrominance[13]=99;
        quantum_chrominance[14]=99;
        quantum_chrominance[15]=99;
        quantum_chrominance[16]=24;
        quantum_chrominance[17]=26;
        quantum_chrominance[18]=56;
        quantum_chrominance[19]=99;
        quantum_chrominance[20]=99;
        quantum_chrominance[21]=99;
        quantum_chrominance[22]=99;
        quantum_chrominance[23]=99;
        quantum_chrominance[24]=47;
        quantum_chrominance[25]=66;
        quantum_chrominance[26]=99;
        quantum_chrominance[27]=99;
        quantum_chrominance[28]=99;
        quantum_chrominance[29]=99;
        quantum_chrominance[30]=99;
        quantum_chrominance[31]=99;
        quantum_chrominance[32]=99;
        quantum_chrominance[33]=99;
        quantum_chrominance[34]=99;
        quantum_chrominance[35]=99;
        quantum_chrominance[36]=99;
        quantum_chrominance[37]=99;
        quantum_chrominance[38]=99;
        quantum_chrominance[39]=99;
        quantum_chrominance[40]=99;
        quantum_chrominance[41]=99;
        quantum_chrominance[42]=99;
        quantum_chrominance[43]=99;
        quantum_chrominance[44]=99;
        quantum_chrominance[45]=99;
        quantum_chrominance[46]=99;
        quantum_chrominance[47]=99;
        quantum_chrominance[48]=99;
        quantum_chrominance[49]=99;
        quantum_chrominance[50]=99;
        quantum_chrominance[51]=99;
        quantum_chrominance[52]=99;
        quantum_chrominance[53]=99;
        quantum_chrominance[54]=99;
        quantum_chrominance[55]=99;
        quantum_chrominance[56]=99;
        quantum_chrominance[57]=99;
        quantum_chrominance[58]=99;
        quantum_chrominance[59]=99;
        quantum_chrominance[60]=99;
        quantum_chrominance[61]=99;
        quantum_chrominance[62]=99;
        quantum_chrominance[63]=99;

        for (j = 0; j < 64; j++)
        {
                temp = (quantum_chrominance[j] * Quality + 50) / 100;
                if ( temp <= 0) temp = 1;
                if (temp >= 255) temp = 255;
                quantum_chrominance[j] = temp;
        }
        index = 0;
        for (i = 0; i < 8; i++) {
                for (j = 0; j < 8; j++) {
// The divisors for the LL&M method (the slow integer method used in
// jpeg 6a library).  This method is currently (04/04/98) incompletely
// implemented.
//                        DivisorsChrominance[index] = ((double) quantum_chrominance[index]) << 3;
// The divisors for the AAN method (the float method used in jpeg 6a library.
                        DivisorsChrominance[index] = (BIGFP) ((BIGFP)1.0/((BIGFP) quantum_chrominance[index] * AANscaleFactor[i] * AANscaleFactor[j] * (BIGFP)8.0));
                        index++;
                }
        }
    }

    /*
     * This method preforms forward DCT on a block of image data using
     * the literal method specified for a 2-D Discrete Cosine Transform.
     * It is included as a curiosity and can give you an idea of the
     * difference in the compression result (the resulting image quality)
     * by comparing its output to the output of the AAN method below.
     * It is ridiculously inefficient.
     */

// For now the final output is unusable.  The associated quantization step
// needs some tweaking.  If you get this part working, please let me know.

    void DCT::forwardDCTExtreme(float input[8][8], BIGFP output[8][8])
    {
        BIGFP tmp0, tmp1, tmp2, tmp3, tmp4, tmp5, tmp6, tmp7;
        BIGFP tmp10, tmp11, tmp12, tmp13;
        BIGFP z1, z2, z3, z4, z5, z11, z13;
        int i;
        int j;
        int v, u, x, y;
        for (v = 0; v < 8; v++) 
        {
                for (u = 0; u < 8; u++) 
                {
                        for (x = 0; x < 8; x++) 
                        {
                                for (y = 0; y < 8; y++) 
                                {
                                        output[v][u] += ((BIGFP)input[x][y])*cos(((BIGFP)(2*x + 1)*(BIGFP)u*PI)/(BIGFP)16)*cos(((BIGFP)(2*y + 1)*(BIGFP)v*PI)/(BIGFP)16);
                                }
                        }
                        output[v][u] *= (BIGFP)(0.25)*((u == 0) ? ((BIGFP)1.0/sqrt(2)) : (BIGFP) 1.0)*((v == 0) ? ((BIGFP)1.0/sqrt(2)) : (BIGFP) 1.0);
                }
        }
    }


    /*
     * This method preforms a DCT on a block of image data using the AAN
     * method as implemented in the IJG Jpeg-6a library.
     */
     void DCT::forwardDCT(float input[8][8], BIGFP output[8][8])
    {
//        double output[][] = new double[N][N];
        BIGFP tmp0, tmp1, tmp2, tmp3, tmp4, tmp5, tmp6, tmp7;
        BIGFP tmp10, tmp11, tmp12, tmp13;
        BIGFP z1, z2, z3, z4, z5, z11, z13;
        int i;
        int j;

// Subtracts 128 from the input values
        for (i = 0; i < 8; i++)
        {
                for(j = 0; j < 8; j++)
                {
                        output[i][j] = ((BIGFP)input[i][j] - (BIGFP)128.0);
//                        input[i][j] -= 128;

                }
        }

        for (i = 0; i < 8; i++) {
                tmp0 = output[i][0] + output[i][7];
                tmp7 = output[i][0] - output[i][7];
                tmp1 = output[i][1] + output[i][6];
                tmp6 = output[i][1] - output[i][6];
                tmp2 = output[i][2] + output[i][5];
                tmp5 = output[i][2] - output[i][5];
                tmp3 = output[i][3] + output[i][4];
                tmp4 = output[i][3] - output[i][4];

                tmp10 = tmp0 + tmp3;
                tmp13 = tmp0 - tmp3;
                tmp11 = tmp1 + tmp2;
                tmp12 = tmp1 - tmp2;

                output[i][0] = tmp10 + tmp11;
                output[i][4] = tmp10 - tmp11;

                z1 = (tmp12 + tmp13) * (BIGFP) 0.707106781;
                output[i][2] = tmp13 + z1;
                output[i][6] = tmp13 - z1;

                tmp10 = tmp4 + tmp5;
                tmp11 = tmp5 + tmp6;
                tmp12 = tmp6 + tmp7;

                z5 = (tmp10 - tmp12) * (BIGFP) 0.382683433;
                z2 = ((BIGFP) 0.541196100) * tmp10 + z5;
                z4 = ((BIGFP) 1.306562965) * tmp12 + z5;
                z3 = tmp11 * ((BIGFP) 0.707106781);

                z11 = tmp7 + z3;
                z13 = tmp7 - z3;

                output[i][5] = z13 + z2;
                output[i][3] = z13 - z2;
                output[i][1] = z11 + z4;
                output[i][7] = z11 - z4;
        }

        for (i = 0; i < 8; i++) {
                tmp0 = output[0][i] + output[7][i];
                tmp7 = output[0][i] - output[7][i];
                tmp1 = output[1][i] + output[6][i];
                tmp6 = output[1][i] - output[6][i];
                tmp2 = output[2][i] + output[5][i];
                tmp5 = output[2][i] - output[5][i];
                tmp3 = output[3][i] + output[4][i];
                tmp4 = output[3][i] - output[4][i];

                tmp10 = tmp0 + tmp3;
                tmp13 = tmp0 - tmp3;
                tmp11 = tmp1 + tmp2;
                tmp12 = tmp1 - tmp2;

                output[0][i] = tmp10 + tmp11;
                output[4][i] = tmp10 - tmp11;

                z1 = (tmp12 + tmp13) * (BIGFP) 0.707106781;
                output[2][i] = tmp13 + z1;
                output[6][i] = tmp13 - z1;

                tmp10 = tmp4 + tmp5;
                tmp11 = tmp5 + tmp6;
                tmp12 = tmp6 + tmp7;

                z5 = (tmp10 - tmp12) * (BIGFP) 0.382683433;
                z2 = ((BIGFP) 0.541196100) * tmp10 + z5;
                z4 = ((BIGFP) 1.306562965) * tmp12 + z5;
                z3 = tmp11 * ((BIGFP) 0.707106781);

                z11 = tmp7 + z3;
                z13 = tmp7 - z3;

                output[5][i] = z13 + z2;
                output[3][i] = z13 - z2;
                output[1][i] = z11 + z4;
                output[7][i] = z11 - z4;
        }

    }
     
     /**
      * just for step by step migration to linear array
      * @param input
      * @param output
      */     
     void DCT::forwardDCT(float* input, BIGFP output[8][8])
    {
//        double output[][] = new double[N][N];
        BIGFP tmp0, tmp1, tmp2, tmp3, tmp4, tmp5, tmp6, tmp7;
        BIGFP tmp10, tmp11, tmp12, tmp13;
        BIGFP z1, z2, z3, z4, z5, z11, z13;
        int i;
        int j;

// Subtracts 128 from the input values
        for (i = 0; i < 8; i++)
        {
                for(j = 0; j < 8; j++)
                {
                        output[i][j] = ((BIGFP)input[i*8+j] - (BIGFP)128.0);
//                        input[i][j] -= 128;

                }
        }

        for (i = 0; i < 8; i++) {
                tmp0 = output[i][0] + output[i][7];
                tmp7 = output[i][0] - output[i][7];
                tmp1 = output[i][1] + output[i][6];
                tmp6 = output[i][1] - output[i][6];
                tmp2 = output[i][2] + output[i][5];
                tmp5 = output[i][2] - output[i][5];
                tmp3 = output[i][3] + output[i][4];
                tmp4 = output[i][3] - output[i][4];

                tmp10 = tmp0 + tmp3;
                tmp13 = tmp0 - tmp3;
                tmp11 = tmp1 + tmp2;
                tmp12 = tmp1 - tmp2;

                output[i][0] = tmp10 + tmp11;
                output[i][4] = tmp10 - tmp11;

                z1 = (tmp12 + tmp13) * (BIGFP) 0.707106781;
                output[i][2] = tmp13 + z1;
                output[i][6] = tmp13 - z1;

                tmp10 = tmp4 + tmp5;
                tmp11 = tmp5 + tmp6;
                tmp12 = tmp6 + tmp7;

                z5 = (tmp10 - tmp12) * (BIGFP) 0.382683433;
                z2 = ((BIGFP) 0.541196100) * tmp10 + z5;
                z4 = ((BIGFP) 1.306562965) * tmp12 + z5;
                z3 = tmp11 * ((BIGFP) 0.707106781);

                z11 = tmp7 + z3;
                z13 = tmp7 - z3;

                output[i][5] = z13 + z2;
                output[i][3] = z13 - z2;
                output[i][1] = z11 + z4;
                output[i][7] = z11 - z4;
        }

        for (i = 0; i < 8; i++) {
                tmp0 = output[0][i] + output[7][i];
                tmp7 = output[0][i] - output[7][i];
                tmp1 = output[1][i] + output[6][i];
                tmp6 = output[1][i] - output[6][i];
                tmp2 = output[2][i] + output[5][i];
                tmp5 = output[2][i] - output[5][i];
                tmp3 = output[3][i] + output[4][i];
                tmp4 = output[3][i] - output[4][i];

                tmp10 = tmp0 + tmp3;
                tmp13 = tmp0 - tmp3;
                tmp11 = tmp1 + tmp2;
                tmp12 = tmp1 - tmp2;

                output[0][i] = tmp10 + tmp11;
                output[4][i] = tmp10 - tmp11;

                z1 = (tmp12 + tmp13) * (BIGFP) 0.707106781;
                output[2][i] = tmp13 + z1;
                output[6][i] = tmp13 - z1;

                tmp10 = tmp4 + tmp5;
                tmp11 = tmp5 + tmp6;
                tmp12 = tmp6 + tmp7;

                z5 = (tmp10 - tmp12) * (BIGFP) 0.382683433;
                z2 = ((BIGFP) 0.541196100) * tmp10 + z5;
                z4 = ((BIGFP) 1.306562965) * tmp12 + z5;
                z3 = tmp11 * ((BIGFP) 0.707106781);

                z11 = tmp7 + z3;
                z13 = tmp7 - z3;

                output[5][i] = z13 + z2;
                output[3][i] = z13 - z2;
                output[1][i] = z11 + z4;
                output[7][i] = z11 - z4;
        }

    }

     void DCT::forwardDCT(float* input, BIGFP* output)
    {
//        double output[][] = new double[N][N];
        BIGFP tmp0, tmp1, tmp2, tmp3, tmp4, tmp5, tmp6, tmp7;
        BIGFP tmp10, tmp11, tmp12, tmp13;
        BIGFP z1, z2, z3, z4, z5, z11, z13;
        int i;
        int j;

// Subtracts 128 from the input values
        for (i = 0; i < 8; i++)
        {
                for(j = 0; j < 8; j++)
                {
                        output[i*8+j] = ((BIGFP)input[i*8+j] - (BIGFP)128.0);
//                        input[i*8+j] -= 128;

                }
        }

        for (i = 0; i < 8; i++) 
        {
                tmp0 = output[i*8+0] + output[i*8+7];
                tmp7 = output[i*8+0] - output[i*8+7];
                tmp1 = output[i*8+1] + output[i*8+6];
                tmp6 = output[i*8+1] - output[i*8+6];
                tmp2 = output[i*8+2] + output[i*8+5];
                tmp5 = output[i*8+2] - output[i*8+5];
                tmp3 = output[i*8+3] + output[i*8+4];
                tmp4 = output[i*8+3] - output[i*8+4];

                tmp10 = tmp0 + tmp3;
                tmp13 = tmp0 - tmp3;
                tmp11 = tmp1 + tmp2;
                tmp12 = tmp1 - tmp2;

                output[i*8+0] = tmp10 + tmp11;
                output[i*8+4] = tmp10 - tmp11;

                z1 = (tmp12 + tmp13) * (BIGFP) 0.707106781;
                output[i*8+2] = tmp13 + z1;
                output[i*8+6] = tmp13 - z1;

                tmp10 = tmp4 + tmp5;
                tmp11 = tmp5 + tmp6;
                tmp12 = tmp6 + tmp7;

                z5 = (tmp10 - tmp12) * (BIGFP) 0.382683433;
                z2 = ((BIGFP) 0.541196100) * tmp10 + z5;
                z4 = ((BIGFP) 1.306562965) * tmp12 + z5;
                z3 = tmp11 * ((BIGFP) 0.707106781);

                z11 = tmp7 + z3;
                z13 = tmp7 - z3;

                output[i*8+5] = z13 + z2;
                output[i*8+3] = z13 - z2;
                output[i*8+1] = z11 + z4;
                output[i*8+7] = z11 - z4;
        }

        for (i = 0; i < 8; i++) 
        {
                tmp0 = output[0*8+i] + output[7*8+i];
                tmp7 = output[0*8+i] - output[7*8+i];
                tmp1 = output[1*8+i] + output[6*8+i];
                tmp6 = output[1*8+i] - output[6*8+i];
                tmp2 = output[2*8+i] + output[5*8+i];
                tmp5 = output[2*8+i] - output[5*8+i];
                tmp3 = output[3*8+i] + output[4*8+i];
                tmp4 = output[3*8+i] - output[4*8+i];

                tmp10 = tmp0 + tmp3;
                tmp13 = tmp0 - tmp3;
                tmp11 = tmp1 + tmp2;
                tmp12 = tmp1 - tmp2;

                output[0*8+i] = tmp10 + tmp11;
                output[4*8+i] = tmp10 - tmp11;

                z1 = (tmp12 + tmp13) * (BIGFP) 0.707106781;
                output[2*8+i] = tmp13 + z1;
                output[6*8+i] = tmp13 - z1;

                tmp10 = tmp4 + tmp5;
                tmp11 = tmp5 + tmp6;
                tmp12 = tmp6 + tmp7;

                z5 = (tmp10 - tmp12) * (BIGFP) 0.382683433;
                z2 = ((BIGFP) 0.541196100) * tmp10 + z5;
                z4 = ((BIGFP) 1.306562965) * tmp12 + z5;
                z3 = tmp11 * ((BIGFP) 0.707106781);

                z11 = tmp7 + z3;
                z13 = tmp7 - z3;

                output[5*8+i] = z13 + z2;
                output[3*8+i] = z13 - z2;
                output[1*8+i] = z11 + z4;
                output[7*8+i] = z11 - z4;
        }

    }

     
     
    /*
    * This method quantitizes data and rounds it to the nearest integer.
    */
    void DCT::quantizeBlock(BIGFP inputData[8][8], int code, int outputData[64])
    {
        int i, j;
        int index;
        index = 0;
        for (i = 0; i < 8; i++)
        {
                for (j = 0; j < 8; j++)
                {
// The second line results in significantly better compression.
                        outputData[index] = (int)(round(inputData[i][j] * (Divisors[code][index])));
//                        outputData[index] = (int)(((inputData[i][j] * (((double[]) (Divisors[code]))[index])) + 16384.5) -16384);
                        index++;
                }
        }

    }
    
    void DCT::quantizeBlock(BIGFP* inputData, int code, int* outputData)
    {
        int i, j;
        int index;
        index = 0;
        for (i = 0; i < 8; i++)
        {
                for (j = 0; j < 8; j++)
                {
// The second line results in significantly better compression.
                        outputData[index] = (int)(round(inputData[i*8+j] * (Divisors[code][index])));
//                        outputData[index] = (int)(((inputData[i][j] * (((double[]) (Divisors[code]))[index])) + 16384.5) -16384);
                        index++;
                }
        }

    }

    /*
    * This is the method for quantizing a block DCT'ed with forwardDCTExtreme
    * This method quantitizes data anｄ rounds it to the nearest integer.
    */
    void DCT::quantizeBlockExtreme(BIGFP inputData[8][8], int code, int outputData[64])
    {
        int i, j;
        int index;
        index = 0;
        for (i = 0; i < 8; i++) {
                for (j = 0; j < 8; j++) {
                        outputData[index] = (int)(round(inputData[i][j] / (BIGFP)(quantum[code][index])));
                        index++;
                }
        }

    }
