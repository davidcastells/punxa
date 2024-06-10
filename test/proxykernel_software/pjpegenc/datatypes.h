// 17/12/2013
// This encoder implemented by David Castells-Rufas (david.castells@uab.cat)
// to do research in parallel implementation of the JPEG encoding algorithm
// The code is implemented in C++ and derived from a Java version, see previous
// author licences below
//
#ifndef DATA_TYPES_H_INCLUDED_
#define DATA_TYPES_H_INCLUDED_

typedef unsigned char byte;

template<typename T>
void arraycopy(T* src, int srcPos, T* dst, int dstPos, int len)
{
	for (int i=0; i < len; i++)
	{
		dst[dstPos+i] = src[srcPos+i];
	}
}

#endif