// 17/12/2013
// This encoder implemented by David Castells-Rufas (david.castells@uab.cat)
// to do research in parallel implementation of the JPEG encoding algorithm
// The code is implemented in C++ and derived from a Java version, see previous
// author licences below
//
// Version 1.0a
// Copyright (C) 1998, James R. Weeks and BioElectroMech.
// Visit BioElectroMech at www.obrador.com.  Email James@obrador.com.

// See license.txt (included below - search for LICENSE.TXT) for details
// about the allowed used of this software.
// This software is based in part on the work of the Independent JPEG Group.
// See IJGreadme.txt (included below - search for IJGREADME.TXT)
// for details about the Independent JPEG Group's license.

// This encoder is inspired by the Java Jpeg encoder by Florian Raemy,
// studwww.eurecom.fr/~raemy.
// It borrows a great deal of code anｄ structure from the Independent
// Jpeg Group's Jpeg 6a library, Copyright Thomas G. Lane.
// See license.txt for details.
#ifndef JPEGENCODER_H_INCLUDED_
#define JPEGENCODER_H_INCLUDED_

#include "BufferedOutputStream.h"
#include "JpegInfo.h"
#include "DCT.h"
#include "Huffman.h"
#include "datatypes.h"
#include "OutputStream.h"
#include "Image.h"

/*
* JpegEncoder - The JPEG main program which performs a jpeg compression of
* an image.
*/

class JpegEncoder 
{
    //Thread runner;
    BufferedOutputStream* m_outStream;
    //Image image;
    JpegInfo* JpegObj;
    Huffman Huf;
    DCT dct;
    int imageHeight, imageWidth;
    int Quality;
    //int code;
    
public:
	 static int jpegNaturalOrder[];

public:
     JpegEncoder(Image* image, int quality, OutputStream* out);
     virtual ~JpegEncoder();
     
     void setQuality(int quality);
     int getQuality();
     void Compress();

     void WriteCompressedData();
     void WriteEOI();
     void WriteHeaders();
    void WriteMarker(byte data[]);
    void WriteArray(byte data[]);
};


#endif







