// 17/12/2013
// This encoder implemented by David Castells-Rufas (david.castells@uab.cat)
// to do research in parallel implementation of the JPEG encoding algorithm
// The code is implemented in C++ and derived from a Java version, see previous
// author licences below
//
#include "Huffman.h"
//#include "JpegEncoder.h"

/**
 * prototype of the class to define jpegNaturalOrder, we can not include
 * JpegEncoder because we have different implementations of it
 */
class JpegEncoder
{
public:
    static int jpegNaturalOrder[];
};

#include <stdio.h>

// This class was modified by James R. Weeks on 3/27/98.

/** It now incorporates Huffman table derivation as in the C jpeg library
 *  from the IJG, Jpeg-6a.
 */

 int Huffman::bitsDCluminance[] = { 0x00, 0, 1, 5, 1, 1,1,1,1,1,0,0,0,0,0,0,0};
     int Huffman::valDCluminance[] = { 0,1,2,3,4,5,6,7,8,9,10,11 };
     int Huffman::bitsDCchrominance[] = { 0x01,0,3,1,1,1,1,1,1,1,1,1,0,0,0,0,0 };
     int Huffman::valDCchrominance[] = { 0,1,2,3,4,5,6,7,8,9,10,11 };
     int Huffman::bitsACluminance[] = {0x10,0,2,1,3,3,2,4,3,5,5,4,4,0,0,1,0x7d };
     int Huffman::valACluminance[] =
        { 0x01, 0x02, 0x03, 0x00, 0x04, 0x11, 0x05, 0x12,
          0x21, 0x31, 0x41, 0x06, 0x13, 0x51, 0x61, 0x07,
          0x22, 0x71, 0x14, 0x32, 0x81, 0x91, 0xa1, 0x08,
          0x23, 0x42, 0xb1, 0xc1, 0x15, 0x52, 0xd1, 0xf0,
          0x24, 0x33, 0x62, 0x72, 0x82, 0x09, 0x0a, 0x16,
          0x17, 0x18, 0x19, 0x1a, 0x25, 0x26, 0x27, 0x28,
          0x29, 0x2a, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39,
          0x3a, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49,
          0x4a, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59,
          0x5a, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69,
          0x6a, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x79,
          0x7a, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89,
          0x8a, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98,
          0x99, 0x9a, 0xa2, 0xa3, 0xa4, 0xa5, 0xa6, 0xa7,
          0xa8, 0xa9, 0xaa, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6,
          0xb7, 0xb8, 0xb9, 0xba, 0xc2, 0xc3, 0xc4, 0xc5,
          0xc6, 0xc7, 0xc8, 0xc9, 0xca, 0xd2, 0xd3, 0xd4,
          0xd5, 0xd6, 0xd7, 0xd8, 0xd9, 0xda, 0xe1, 0xe2,
          0xe3, 0xe4, 0xe5, 0xe6, 0xe7, 0xe8, 0xe9, 0xea,
          0xf1, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6, 0xf7, 0xf8,
          0xf9, 0xfa };
    int Huffman::bitsACchrominance[] = { 0x11,0,2,1,2,4,4,3,4,7,5,4,4,0,1,2,0x77 };;
    int Huffman::valACchrominance[] =
        { 0x00, 0x01, 0x02, 0x03, 0x11, 0x04, 0x05, 0x21,
          0x31, 0x06, 0x12, 0x41, 0x51, 0x07, 0x61, 0x71,
          0x13, 0x22, 0x32, 0x81, 0x08, 0x14, 0x42, 0x91,
          0xa1, 0xb1, 0xc1, 0x09, 0x23, 0x33, 0x52, 0xf0,
          0x15, 0x62, 0x72, 0xd1, 0x0a, 0x16, 0x24, 0x34,
          0xe1, 0x25, 0xf1, 0x17, 0x18, 0x19, 0x1a, 0x26,
          0x27, 0x28, 0x29, 0x2a, 0x35, 0x36, 0x37, 0x38,
          0x39, 0x3a, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48,
          0x49, 0x4a, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58,
          0x59, 0x5a, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68,
          0x69, 0x6a, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78,
          0x79, 0x7a, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87,
          0x88, 0x89, 0x8a, 0x92, 0x93, 0x94, 0x95, 0x96,
          0x97, 0x98, 0x99, 0x9a, 0xa2, 0xa3, 0xa4, 0xa5,
          0xa6, 0xa7, 0xa8, 0xa9, 0xaa, 0xb2, 0xb3, 0xb4,
          0xb5, 0xb6, 0xb7, 0xb8, 0xb9, 0xba, 0xc2, 0xc3,
          0xc4, 0xc5, 0xc6, 0xc7, 0xc8, 0xc9, 0xca, 0xd2,
          0xd3, 0xd4, 0xd5, 0xd6, 0xd7, 0xd8, 0xd9, 0xda,
          0xe2, 0xe3, 0xe4, 0xe5, 0xe6, 0xe7, 0xe8, 0xe9,
          0xea, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6, 0xf7, 0xf8,
          0xf9, 0xfa };

          
    
    /**
     * 
     * @param b dummy parameter to allow a "non active" contrustror 
     * for a more controlled cloning operation
     */
    Huffman::Huffman(bool  b)
    {

    }

/*
    protected Object clone() throws CloneNotSupportedException
    {
        Huffman ret = new Huffman(false);

        ret.bits = this.bits;
        ret.val = this.val;

        ret.DC_matrix = this.DC_matrix;
        ret.AC_matrix = this.AC_matrix;

        ret.bufferPutBits = 0;
        ret.bufferPutBuffer = 0;

        return ret;
    }
*/


    /*
    * The Huffman class constructor
    */
        Huffman::Huffman()
	{
            bits[0] = bitsDCluminance;
            bits[1] = bitsACluminance;
            bits[2] = bitsDCchrominance;
            bits[3] = bitsACchrominance;

            val[0] = valDCluminance;
            val[1] = valACluminance;
            val[2] = valDCchrominance;
            val[3] = valACchrominance;
            initHuf();
	    //code=code;
            
	}

   /**
   * run run length encodes anｄ Huffman encodes the quantized
   * data.
         * @param outStream
         * @param zigzag
         * @param prec  previous DC value
         * @param DCcode
         * @param ACcode
         * @param forceAlign
         * @throws IOException
         */
    void Huffman::run(OutputStream* outStream, int zigzag[], int prec, int DCcode, int ACcode, bool  forceAlign) 
    {
        int FreqValue;
        int ACValue;
        int nbits, k;
        int run;
        int NumOfDCTables = 2;
        int NumOfACTables = 2;

// The DC portion

        FreqValue = ACValue = zigzag[0] - prec;
        if (FreqValue < 0)
        {
            FreqValue = -FreqValue;
            ACValue--;
        }
        nbits = 0;
        while (FreqValue != 0)
        {
            nbits++;
            FreqValue >>= 1;
        }
//        if (nbits > 11) nbits = 11;
        bufferIt(outStream, DC_matrix[DCcode][nbits][0], DC_matrix[DCcode][nbits][1]);

        // The arguments in bufferIt are code and size.
        if (nbits != 0)
        {
            bufferIt(outStream, ACValue, nbits);
        }
        bool stop;


        if (forceAlign)
        {
            // do whatever to fill the buffer
//            System.out.println(">bufferPutBits=" + bufferPutBits );

            // Find code with length 2 and 3
            
            int kitop = 16 - 2 - bufferPutBits;

            if (bufferPutBits == 7)
                stop = true;

            if (kitop == 1)
                // we are not able to put 1 bit
                kitop += 8;

            // the following code puts 2*kitop + 2 bits. since it should be aligned
            // 2*kitop + 2 + bufferPutBits

            while (bufferPutBits != 6)
            {
                bufferIt(outStream, 4, 3);
                bufferIt(outStream, 0, 2);

            }

            //bufferIt(outStream, code2[0], code2[1]);
            //bufferIt(outStream, code3[0], code3[1]);
            
            bufferIt(outStream, AC_matrix[ACcode][0][0], AC_matrix[ACcode][0][1]);
            

//            System.out.println("bufferPutBits=" + bufferPutBits + " after forced zero");
            return;
        }

        // The AC portion

        run = 0;

        for (k = 1; k < 64; k++)
        {
        	if ((FreqValue = zigzag[JpegEncoder::jpegNaturalOrder[k]]) == 0)
            {
                // Ignore zero AC values
                run++;
            }
            else
            {
                while (run > 15)
                {
                    bufferIt(outStream, AC_matrix[ACcode][0xF0][0], AC_matrix[ACcode][0xF0][1]);
                    run -= 16;
                }

                ACValue = FreqValue;
                if (FreqValue < 0)
                {
                    FreqValue = -FreqValue;
                    ACValue--;
                }

                // Compute the number of bits necessary to represent the value
                nbits = 1;
                while ((FreqValue >>= 1) != 0)
                {
                    nbits++;
                }
                int i = (run << 4) + nbits;

                bufferIt(outStream, AC_matrix[ACcode][i][0], AC_matrix[ACcode][i][1]);
                bufferIt(outStream, ACValue, nbits);

                run = 0;

            }
        }

        if (run > 0)
        {
            bufferIt(outStream, AC_matrix[ACcode][0][0], AC_matrix[ACcode][0][1]);
        }

    }

// Uses an integer long (32 bits) buffer to store the Huffman encoded bits
// anｄ sends them to outStream by the byte.

    void Huffman::bufferIt(OutputStream* outStream, int code, int size) 
    {
        int PutBuffer = code;
        int PutBits = bufferPutBits;

        PutBuffer &= (1 << size) - 1;
        PutBits += size;
        PutBuffer <<= 24 - PutBits;
        PutBuffer |= bufferPutBuffer;

        while (PutBits >= 8)
        {
            int c = ((PutBuffer >> 16) & 0xFF);

            outStream->write(c);

            if (c == 0xFF)
            {
                outStream->write(0);
            }
            PutBuffer <<= 8;
            PutBits -= 8;
        }
        bufferPutBuffer = PutBuffer;
        bufferPutBits = PutBits;
    }

    void Huffman::flushBuffer(OutputStream* outStream) 
    {
        int PutBuffer = bufferPutBuffer;
        int PutBits = bufferPutBits;
        
        while (PutBits >= 8)
        {
            int c = ((PutBuffer >> 16) & 0xFF);

            outStream->write(c);

            if (c == 0xFF)
            {
                outStream->write(0);
            }
            PutBuffer <<= 8;
            PutBits -= 8;
        }

        if (PutBits > 0)
        {
            int c = ((PutBuffer >> 16) & 0xFF);
            outStream->write(c);
        }
    }

    /*
    * Initialisation of the Huffman codes for Luminance anｄ Chrominance.
    * This code results in the same tables created in the IJG Jpeg-6a
    * library.
    */

     void Huffman::initHuf()
    {
        
        int p, l, i, lastp, si;
        int code;
        int huffsize[257];
        int huffcode[257];

        /*
        * init of the DC values for the chrominance
        * [][0] is the code   [][1] is the number of bit
        */

        p = 0;
        for (l = 1; l <= 16; l++)
        {
                for (i = 1; i <= bitsDCchrominance[l]; i++)
                {
                        huffsize[p++] = l;
                }
        }
        huffsize[p] = 0;
        lastp = p;

        code = 0;
        si = huffsize[0];
        p = 0;
        while(huffsize[p] != 0)
        {
                while(huffsize[p] == si)
                {
                        huffcode[p++] = code;
                        code++;
                }
                code <<= 1;
                si++;
        }

        for (p = 0; p < lastp; p++)
        {
                DC_matrix[1][valDCchrominance[p]][0] = huffcode[p];
                DC_matrix[1][valDCchrominance[p]][1] = huffsize[p];
        }

        /*
        * Init of the AC hufmann code for the chrominance
        * matrix [][][0] is the code & matrix[][][1] is the number of bit needed
        */

        p = 0;
        for (l = 1; l <= 16; l++)
        {
                for (i = 1; i <= bitsACchrominance[l]; i++)
                {
                        huffsize[p++] = l;
                }
        }
        huffsize[p] = 0;
        lastp = p;

        code = 0;
        si = huffsize[0];
        p = 0;
        while(huffsize[p] != 0)
        {
                while(huffsize[p] == si)
                {
                        huffcode[p++] = code;
                        code++;
                }
                code <<= 1;
                si++;
        }

        for (p = 0; p < lastp; p++)
        {
                AC_matrix[1][valACchrominance[p]][0] = huffcode[p];
                AC_matrix[1][valACchrominance[p]][1] = huffsize[p];
        }

        /*
        * init of the DC values for the luminance
        * [][0] is the code   [][1] is the number of bit
        */
        p = 0;
        for (l = 1; l <= 16; l++)
        {
                for (i = 1; i <= bitsDCluminance[l]; i++)
                {
                        huffsize[p++] = l;
                }
        }
        huffsize[p] = 0;
        lastp = p;

        code = 0;
        si = huffsize[0];
        p = 0;
        while(huffsize[p] != 0)
        {
                while(huffsize[p] == si)
                {
                        huffcode[p++] = code;
                        code++;
                }
                code <<= 1;
                si++;
        }

        for (p = 0; p < lastp; p++)
        {
                DC_matrix[0][valDCluminance[p]][0] = huffcode[p];
                DC_matrix[0][valDCluminance[p]][1] = huffsize[p];
        }

        /*
        * Init of the AC hufmann code for luminance
        * matrix [][][0] is the code & matrix[][][1] is the number of bit
        */

        p = 0;
        for (l = 1; l <= 16; l++)
        {
                for (i = 1; i <= bitsACluminance[l]; i++)
                {
                        huffsize[p++] = l;
                }
        }
        huffsize[p] = 0;
        lastp = p;

        code = 0;
        si = huffsize[0];
        p = 0;
        while(huffsize[p] != 0)
        {
                while(huffsize[p] == si)
                {
                        huffcode[p++] = code;
                        code++;
                }
                code <<= 1;
                si++;
        }
        for (int q = 0; q < lastp; q++)
        {
                AC_matrix[0][valACluminance[q]][0] = huffcode[q];
                AC_matrix[0][valACluminance[q]][1] = huffsize[q];
        }

    }

//    private int[] findCode(int[][] codes, int len)
//    {
//        int[] codeRun = null;
//
//        for (int ki=0; (ki < codes.length); ki++)
//        {
//            codeRun = codes[ki];
//
//            if (codeRun[1] == len)
//                return codeRun;
//
//        }
//
//        return null;
//    }

