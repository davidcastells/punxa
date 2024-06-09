/* 
 * File:   ByteArrayOutputStream.h
 * Author: dcr
 *
 * Created on July 13, 2015, 8:01 PM
 */

#ifndef BYTEARRAYOUTPUTSTREAM_H
#define	BYTEARRAYOUTPUTSTREAM_H

#include "OutputStream.h"
#include "datatypes.h"

class ByteArrayOutputStream : public OutputStream
{
public:
    ByteArrayOutputStream(int size);
    virtual ~ByteArrayOutputStream();
public:
    virtual void write(int c); 
    virtual void write(byte data[], int offset, int len);
    virtual void close();

protected:
    byte* buf;
    int count;
    int capacity;
};

#endif	/* BYTEARRAYOUTPUTSTREAM_H */

