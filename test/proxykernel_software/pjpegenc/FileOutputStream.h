// 17/12/2013
// This encoder implemented by David Castells-Rufas (david.castells@uab.cat)
// to do research in parallel implementation of the JPEG encoding algorithm
// The code is implemented in C++ and derived from a Java version, see previous
// author licences below
//
#ifndef FILEOUTPUTSTREAM_H_INCLUDED_
#define FILEOUTPUTSTREAM_H_INCLUDED_

#include "OutputStream.h"
#include "datatypes.h"

#include <stdio.h>

class FileOutputStream : public OutputStream
{
	FILE* m_fp;
	
public:
	FileOutputStream(char* filename);
	~FileOutputStream();
	
public:
	virtual void flush();
	virtual void write(byte data[], int offset, int len);
	virtual void write(int c); 
        virtual void close();
};

#endif