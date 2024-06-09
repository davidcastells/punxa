// 17/12/2013
// This encoder implemented by David Castells-Rufas (david.castells@uab.cat)
// to do research in parallel implementation of the JPEG encoding algorithm
// The code is implemented in C++ and derived from a Java version, see previous
// author licences below
//
// Version 1.0a
// Copyright (C) 1998, James R. Weeks and BioElectroMech.
// Visit BioElectroMech at www.obrador.com.  Email James@obrador.com.
//
// See license.txt (included below - search for LICENSE.TXT) for details
// about the allowed used of this software.
// This software is based in part on the work of the Independent JPEG Group.
// See IJGreadme.txt (included below - search for IJGREADME.TXT)
// for details about the Independent JPEG Group's license.
//
// This encoder is inspired by the Java Jpeg encoder by Florian Raemy,
// studwww.eurecom.fr/~raemy.
// It borrows a great deal of code and structure from the Independent
// Jpeg Group's Jpeg 6a library, Copyright Thomas G. Lane.
// See license.txt for details.

#include "JpegEncoder.h"
#include "datatypes.h"
#include "globals.h"

#include <math.h>
#include <stdio.h>

int JpegEncoder::jpegNaturalOrder[] =
    {
          0,  1,  8, 16,  9,  2,  3, 10,
         17, 24, 32, 25, 18, 11,  4,  5,
         12, 19, 26, 33, 40, 48, 41, 34,
         27, 20, 13,  6,  7, 14, 21, 28,
         35, 42, 49, 56, 57, 50, 43, 36,
         29, 22, 15, 23, 30, 37, 44, 51,
         58, 59, 52, 45, 38, 31, 39, 46,
         53, 60, 61, 54, 47, 55, 62, 63,
        };

    /**
     *
     * @param image the image should be ready
     * @param quality value between 0 and 100. 0 means the lowest quality and 100 mean the highest quality
     * @param out
     */
    JpegEncoder::JpegEncoder(Image* image, int quality, OutputStream* out)
    {

        /*
        * Quality of the image.
        * 0 to 100 anｄ from bad image quality, high compression to good
        * image quality low compression
        */
        //Quality=quality;

        /*
        * Getting picture information
        * It takes the Width, Height anｄ RGB scans of the image.
        */
        JpegObj = new JpegInfo(image);
        
        imageHeight=JpegObj->imageHeight;
        imageWidth=JpegObj->imageWidth;
        m_outStream = new BufferedOutputStream(out);
        dct.init(quality);
        //Huf=new Huffman();
    }
    
    JpegEncoder::~JpegEncoder()
    { 
        delete JpegObj;
        delete m_outStream;
    }

     void JpegEncoder::setQuality(int quality) {
        dct.init(quality);
    }

     int JpegEncoder::getQuality() {
        return Quality;
    }

     void JpegEncoder::Compress() 
    {
        if (verbose) printf("WriteHeaders\n");
        WriteHeaders();

        if (verbose) printf("WriteCompressedData\n");
        WriteCompressedData();

        if (verbose) printf("WriteEOI\n");
        WriteEOI();

        if (verbose) printf("Flush\n");
        m_outStream->flush();
    }

     void JpegEncoder::WriteCompressedData() 
    {
        BufferedOutputStream* outStream = m_outStream;
        int offset, i, j, r, c,a ,b, temp = 0;
        int comp, xpos, ypos, xblockoffset, yblockoffset;
        float dctArray1[8][8];
        BIGFP dctArray2[8][8];
        int dctArray3[8*8];

        /*
         * This method controls the compression of the image.
         * Starting at the upper left of the image, it compresses 8x8 blocks
         * of data until the entire image has been compressed.
         */

        int lastDCvalue[NUMBER_OF_COMPONENTS];

        for (int i=0; i < NUMBER_OF_COMPONENTS; i++) lastDCvalue[i] = 0;

        //int zeroArray[64]; // initialized to hold all zeros
        int Width = 0, Height = 0;
        int nothing = 0;
        int MinBlockWidth, MinBlockHeight;
// This initial setting of MinBlockWidth anｄ MinBlockHeight is done to
// ensure they start with values larger than will actually be the case.
        MinBlockWidth = ((imageWidth%8 != 0) ? (int) (floor((BIGFP) imageWidth/8.0) + 1)*8 : imageWidth);
        MinBlockHeight = ((imageHeight%8 != 0) ? (int) (floor((BIGFP) imageHeight/8.0) + 1)*8: imageHeight);
        
        for (comp = 0; comp < NUMBER_OF_COMPONENTS; comp++)
        {
                MinBlockWidth = std::min(MinBlockWidth, JpegObj->BlockWidth[comp]);
                MinBlockHeight = std::min(MinBlockHeight, JpegObj->BlockHeight[comp]);
        }
        xpos = 0;
        for (r = 0; r < MinBlockHeight; r++)
        {
           for (c = 0; c < MinBlockWidth; c++)
           {
               xpos = c*8;
               ypos = r*8;
   
               for (comp = 0; comp < NUMBER_OF_COMPONENTS; comp++)
               {
                  Width = JpegObj->BlockWidth[comp];
                  Height = JpegObj->BlockHeight[comp];
                 
                  Matrix<float>* inputArray = JpegObj->Components[comp];

                  for(i = 0; i < JpegObj->VsampFactor[comp]; i++)
                  {
                     for(j = 0; j < JpegObj->HsampFactor[comp]; j++)
                     {
                        xblockoffset = j * 8;
                        yblockoffset = i * 8;
                        for (a = 0; a < 8; a++)
                        {
                           for (b = 0; b < 8; b++)
                           {
				dctArray1[a][b] = inputArray->get(ypos + yblockoffset + a, xpos + xblockoffset + b);
			   }
                        }
// The following code commented out because on some images this technique
// results in poor right anｄ bottom borders.
//                        if ((!JpegObj.lastColumnIsDummy[comp] || c < Width - 1) && (!JpegObj.lastRowIsDummy[comp] || r < Height - 1)) {

                        dct.forwardDCT(dctArray1, dctArray2);
                        dct.quantizeBlock(dctArray2, JpegObj->QtableNumber[comp], dctArray3);
//                        }
//                        else {
//                           zeroArray[0] = dctArray3[0];
//                           zeroArray[0] = lastDCvalue[comp];
//                           dctArray3 = zeroArray;
//                        }
                        Huf.run(outStream, dctArray3, lastDCvalue[comp], JpegObj->DCtableNumber[comp], JpegObj->ACtableNumber[comp], false);
                        lastDCvalue[comp] = dctArray3[0];
                     }
                  }
               }
            }
        }
        Huf.flushBuffer(outStream);
    }

     void JpegEncoder::WriteEOI() 
    {
        byte EOI[] = {(byte) 0xFF, (byte) 0xD9};
        WriteMarker(EOI);
    }

    
     
    void JpegEncoder::WriteHeaders()
    {
        if (verbose)
            printf("Write headers\n");
        
        int i, j, index, offset, length;

// the SOI marker
        byte SOI[] = {(byte) 0xFF, (byte) 0xD8};
        WriteMarker(SOI);

// The order of the following headers is quiet inconsequential.
// the JFIF header
        byte JFIF[18];
        JFIF[0] = (byte) 0xff;
        JFIF[1] = (byte) 0xe0;
        JFIF[2] = (byte) 0x00;
        JFIF[3] = (byte) 0x10;
        JFIF[4] = (byte) 0x4a;
        JFIF[5] = (byte) 0x46;
        JFIF[6] = (byte) 0x49;
        JFIF[7] = (byte) 0x46;
        JFIF[8] = (byte) 0x00;
        JFIF[9] = (byte) 0x01;
        JFIF[10] = (byte) 0x00;
        JFIF[11] = (byte) 0x00;
        JFIF[12] = (byte) 0x00;
        JFIF[13] = (byte) 0x01;
        JFIF[14] = (byte) 0x00;
        JFIF[15] = (byte) 0x01;
        JFIF[16] = (byte) 0x00;
        JFIF[17] = (byte) 0x00;
        WriteArray(JFIF);

// Comment Header
	std::string comment = JpegObj->getComment();
        length = comment.length();
        byte COM[length + 4];
        COM[0] = (byte) 0xFF;
        COM[1] = (byte) 0xFE;
        COM[2] = (byte) ((length >> 8) & 0xFF);
        COM[3] = (byte) (length & 0xFF);
        arraycopy((byte*) JpegObj->Comment.data(), 0, COM, 4, JpegObj->Comment.length());
        WriteArray(COM);

// The DQT header
// 0 is the luminance index anｄ 1 is the chrominance index
        byte DQT[134];
        DQT[0] = (byte) 0xFF;
        DQT[1] = (byte) 0xDB;
        DQT[2] = (byte) 0x00;
        DQT[3] = (byte) 0x84;
        offset = 4;
        for (i = 0; i < 2; i++) 
        {
                DQT[offset++] = (byte) ((0 << 4) + i);
                        
                int* tempArray = dct.quantum[i];
                for (j = 0; j < 64; j++) 
                {
                        DQT[offset++] = (byte) tempArray[jpegNaturalOrder[j]];
                }
        }
        WriteArray(DQT);

// Start of Frame Header
        byte SOF[19];
        SOF[0] = (byte) 0xFF;
        SOF[1] = (byte) 0xC0;
        SOF[2] = (byte) 0x00;
        SOF[3] = (byte) 17;
        SOF[4] = (byte) JpegObj->Precision;
        SOF[5] = (byte) ((JpegObj->imageHeight >> 8) & 0xFF);
        SOF[6] = (byte) ((JpegObj->imageHeight) & 0xFF);
        SOF[7] = (byte) ((JpegObj->imageWidth >> 8) & 0xFF);
        SOF[8] = (byte) ((JpegObj->imageWidth) & 0xFF);
        SOF[9] = (byte) NUMBER_OF_COMPONENTS;
        index = 10;
        for (i = 0; i < SOF[9]; i++) 
        {
                SOF[index++] = (byte) JpegObj->CompID[i];
                SOF[index++] = (byte) ((JpegObj->HsampFactor[i] << 4) + JpegObj->VsampFactor[i]);
                SOF[index++] = (byte) JpegObj->QtableNumber[i];
        }
        WriteArray(SOF);

// The DHT Header
        int bytes, temp, oldindex, intermediateindex;
        length = 2;
        index = 4;
        oldindex = 4;
        byte DHT1[17];
        byte* DHT4 = new byte[4];
        DHT4[0] = (byte) 0xFF;
        DHT4[1] = (byte) 0xC4;
        for (i = 0; i < 4; i++ ) 
        {
                bytes = 0;
                DHT1[index++ - oldindex] = (byte) Huf.bits[i][0];
                for (j = 1; j < 17; j++) 
                {
                        temp = Huf.bits[i][j];
                        DHT1[index++ - oldindex] =(byte) temp;
                        bytes += temp;
                }
                intermediateindex = index;

                byte DHT2[bytes];
                for (j = 0; j < bytes; j++) {
                        DHT2[index++ - intermediateindex] = (byte) Huf.val[i][j];
                }

                byte* DHT3 = new byte[index];
                arraycopy(DHT4, 0, DHT3, 0, oldindex);
                arraycopy(DHT1, 0, DHT3, oldindex, 17);
                arraycopy(DHT2, 0, DHT3, oldindex + 17, bytes);
                
                delete [] DHT4;
                DHT4 = DHT3;
                oldindex = index;
        }
        DHT4[2] = (byte) (((index - 2) >> 8)& 0xFF);
        DHT4[3] = (byte) ((index -2) & 0xFF);
        WriteArray(DHT4);

        delete [] DHT4;

// Start of Scan Header
        byte SOS[14];
        SOS[0] = (byte) 0xFF;
        SOS[1] = (byte) 0xDA;
        SOS[2] = (byte) 0x00;
        SOS[3] = (byte) 12;
        SOS[4] = (byte) NUMBER_OF_COMPONENTS;
        index = 5;
        for (i = 0; i < SOS[4]; i++)
        {
                SOS[index++] = (byte) JpegObj->CompID[i];
                SOS[index++] = (byte) ((JpegObj->DCtableNumber[i] << 4) + JpegObj->ACtableNumber[i]);
        }
        SOS[index++] = (byte) JpegObj->Ss;
        SOS[index++] = (byte) JpegObj->Se;
        SOS[index++] = (byte) ((JpegObj->Ah << 4) + JpegObj->Al);
        WriteArray(SOS);

    }

    void JpegEncoder::WriteMarker(byte data[])
    {
	m_outStream->write(data, 0, 2);

    }

    void JpegEncoder::WriteArray(byte data[])
    {
        int i, length;
                
	length = (((data[2] & 0xFF)) << 8) + (data[3] & 0xFF) + 2;
	m_outStream->write(data, 0, length);

    }









