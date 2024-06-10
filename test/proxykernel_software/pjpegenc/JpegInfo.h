// 17/12/2013
// This encoder implemented by David Castells-Rufas (david.castells@uab.cat)
// to do research in parallel implementation of the JPEG encoding algorithm
// The code is implemented in C++ and derived from a Java version, see previous
// author licences below
//

#ifndef JPEGINFO_H_INCLUDED_
#define JPEGINFO_H_INCLUDED_

#include <string>

#include "Image.h"
#include "Matrix.h"


/*
 * JpegInfo - Given an image, sets default information about it anｄ divides
 * it into its constituant components, downsizing those that need to be.
 */
#define NUMBER_OF_COMPONENTS  3

class JpegInfo
{
public:
    std::string Comment;
    Image* imageobj;
     int imageHeight;
     int imageWidth;


// the following are set as the default
     int Precision;
     
     
     Matrix<float>* Components[NUMBER_OF_COMPONENTS];

     int CompID[NUMBER_OF_COMPONENTS];
     int HsampFactor[NUMBER_OF_COMPONENTS];
     int VsampFactor[NUMBER_OF_COMPONENTS];
     int QtableNumber[NUMBER_OF_COMPONENTS];
     int DCtableNumber[NUMBER_OF_COMPONENTS];
     int ACtableNumber[NUMBER_OF_COMPONENTS];
     bool lastColumnIsDummy[NUMBER_OF_COMPONENTS];
     bool  lastRowIsDummy[NUMBER_OF_COMPONENTS];
     
     int Ss;
     
     int Se;
     
     int Ah;
     
     int Al;
     
     int compWidth[NUMBER_OF_COMPONENTS];
     int compHeight[NUMBER_OF_COMPONENTS];
     int BlockWidth[NUMBER_OF_COMPONENTS];
     int BlockHeight[NUMBER_OF_COMPONENTS];
     
     int MaxHsampFactor;
     int MaxVsampFactor;


public:
	JpegInfo();
	~JpegInfo();

	JpegInfo(Image* image);

	void setComment(std::string comment);

	std::string getComment();

    /*
     * This method creates anｄ fills three arrays, Y, Cb, anｄ Cr using the
     * input image.
     */

private:
	void getYCCArray();

//    float[][] DownSample(float[][] C, int comp);
};

#endif
