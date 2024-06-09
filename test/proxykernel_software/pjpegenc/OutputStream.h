// 17/12/2013
// This encoder implemented by David Castells-Rufas (david.castells@uab.cat)
// to do research in parallel implementation of the JPEG encoding algorithm
// The code is implemented in C++ and derived from a Java version, see previous
// author licences below
//
#ifndef OUTPUTSTREAM_H_INCLUDED_
#define OUTPUTSTREAM_H_INCLUDED_

#include "datatypes.h"

class OutputStream
{
public:
	virtual void flush();
	virtual void write(byte data[], int offset, int len);
	virtual void write(int c) = 0; 
        virtual void close() = 0;
};


#endif
