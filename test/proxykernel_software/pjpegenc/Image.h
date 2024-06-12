// 17/12/2013
// This encoder implemented by David Castells-Rufas (david.castells@uab.cat)
// to do research in parallel implementation of the JPEG encoding algorithm
// The code is implemented in C++ and derived from a Java version, see previous
// author licences below
//
#ifndef DATATYPES_H_INCLUDED_
#define DATATYPES_H_INCLUDED_

class Image
{
public:
	virtual int getWidth() = 0;
	virtual int getHeight() = 0;

    // not compliant with java.awt.Image
    virtual int getRGB(int x, int y) = 0;
    virtual void getRGB(int x, int y, int* r, int* g, int* b) = 0;

};



#endif
