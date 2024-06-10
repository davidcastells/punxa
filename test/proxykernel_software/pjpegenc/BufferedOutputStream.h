// 17/12/2013
// This encoder implemented by David Castells-Rufas (david.castells@uab.cat)
// to do research in parallel implementation of the JPEG encoding algorithm
// The code is implemented in C++ and derived from a Java version, see previous
// author licences below
//
#ifndef BUFFEREDOUTPUTSTREAM_H_INCLUDED_
#define BUFFEREDOUTPUTSTREAM_H_INCLUDED_

#include "OutputStream.h"
#include "datatypes.h"

class BufferedOutputStream : public OutputStream
{
	OutputStream* m_out;
	byte* m_buffer;
	int m_count;
	int m_size;
public:
	BufferedOutputStream(OutputStream* out);
	~BufferedOutputStream();
	
public:
	virtual void flush();
	virtual void write(byte data[], int offset, int len);
	virtual void write(int c); 
        virtual void close();
	
};

#endif

