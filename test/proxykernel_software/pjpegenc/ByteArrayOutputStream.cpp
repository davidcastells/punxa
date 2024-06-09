// 13/07/2015
// This encoder implemented by David Castells-Rufas (david.castells@uab.cat)
// to do research in parallel implementation of the JPEG encoding algorithm
// The code is implemented in C++ and derived from a Java version
//
#include "ByteArrayOutputStream.h"

#include <stdio.h>

ByteArrayOutputStream::ByteArrayOutputStream(int size)
{
    count = 0;
    buf = new byte[size];
    capacity = size;
}



ByteArrayOutputStream::~ByteArrayOutputStream() 
{
    delete [] buf;
}


void ByteArrayOutputStream::write(int c)
{
	if (count < capacity)
	{
		buf[count++] = c;
	}
	else
	{
            printf("ERROR: buffer overrun\n");
	}
}


void ByteArrayOutputStream::write(byte data[], int offset, int len)
{
    int end = offset + len;
    
    for (int i=offset; i < end; i++)
    {
        buf[count++] = data[i];
    }
}

void ByteArrayOutputStream::close()
{
    count = 0;
}