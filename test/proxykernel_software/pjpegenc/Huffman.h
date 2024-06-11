// 17/12/2013
// This encoder implemented by David Castells-Rufas (david.castells@uab.cat)
// to do research in parallel implementation of the JPEG encoding algorithm
// The code is implemented in C++ and derived from a Java version, see previous
// author licences below
//


#ifndef HUFFMAN_H_INCLUDED_
#define HUFFMAN_H_INCLUDED_

// This class was modified by James R. Weeks on 3/27/98.
#include "OutputStream.h"

#include <vector>


/** It now incorporates Huffman table derivation as in the C jpeg library
 *  from the IJG, Jpeg-6a.
 */
class Huffman 
{
    static int bitsDCluminance[];
    static int valDCluminance[];
    static int bitsDCchrominance[];
    static int valDCchrominance[];
    static int bitsACluminance[];
    static int valACluminance[];
    static int bitsACchrominance[];
    static int valACchrominance[];
    
public:
    int* bits[4];
    int* val[4];

    int bufferPutBits;
    int bufferPutBuffer;

public:
	int  DC_matrix[2][12][2];
        int  AC_matrix[2][255][2];
        
    
    /**
     * 
     * @param b dummy parameter to allow a "non active" contrustror 
     * for a more controlled cloning operation
     */
private:
	Huffman(bool b);


protected:
	Huffman clone();



    /*
    * The Huffman class constructor
    */
public:
	Huffman();

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
 public:
 	 void run(OutputStream* outStream, int zigzag[], int prec, int DCcode, int ACcode, bool forceAlign);

// Uses an integer long (32 bits) buffer to store the Huffman encoded bits
// anｄ sends them to outStream by the byte.

    void bufferIt(OutputStream* outStream, int code, int size);

    void flushBuffer(OutputStream* outStream);

    /*
    * Initialisation of the Huffman codes for Luminance anｄ Chrominance.
    * This code results in the same tables created in the IJG Jpeg-6a
    * library.
    */

public: void initHuf();

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

};

#endif