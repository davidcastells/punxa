// 17/12/2013
// This encoder implemented by David Castells-Rufas (david.castells@uab.cat)
// to do research in parallel implementation of the JPEG encoding algorithm
// The code is implemented in C++ and derived from a Java version, see previous
// author licences below
//
#ifndef MATRIX_H_INCLUDED_
#define MATRIX_H_INCLUDED_

#include "datatypes.h"

template<typename T>
class Matrix
{
	T* m_data;
	int m_w;
	int m_h;

public:
	Matrix(int h, int w )
	{
		m_w = w;
		m_h = h;
		m_data = new T[w*h];
	}
        
        virtual ~Matrix()
        {
            delete[] m_data;
        }
	
	T get(int y, int x)
	{
		return m_data[m_w*y+x];
	}
	
	void put(int y, int x, T v)
	{
		m_data[m_w*y+x] = v;
	}
};

template<typename T>
class Matrix4D
{
	T* m_data;
	int m_d1;
	int m_d2;
        int m_d3;
        int m_d4;
        

public:
	Matrix4D(int d1, int d2, int d3, int d4)
	{
            m_d1 = d1;
            m_d2 = d2;
            m_d3 = d3;
            m_d4 = d4;
            
		
            m_data = new T[d1*d2*d3*d4];
	}
        
        virtual ~Matrix4D()
        {
            delete[] m_data;
        }
	
	T get(int i1, int i2, int i3, int i4)
	{
            return m_data[(i1*m_d2*m_d3*m_d4)+(i2*m_d3*m_d4)+(i3*m_d4)+i4];
	}
	
	void put(int i1, int i2, int i3, int i4, T v)
	{
            m_data[(i1*m_d2*m_d3*m_d4)+(i2*m_d3*m_d4)+(i3*m_d4)+i4] = v;
	}
        
        T* get3DRef(int i1, int i2, int i3)
        {
            return &m_data[(i1*m_d2*m_d3*m_d4)+(i2*m_d3*m_d4)+(i3*m_d4)];
        }
};

template<typename T>
class Matrix5D
{
	T* m_data;
	int m_d1;
	int m_d2;
        int m_d3;
        int m_d4;
        int m_d5;

public:
	Matrix5D(int d1, int d2, int d3, int d4, int d5)
	{
            m_d1 = d1;
            m_d2 = d2;
            m_d3 = d3;
            m_d4 = d4;
            m_d5 = d5;
		
            
            m_data = new T[d1*d2*d3*d4*d5];
	}
        
        virtual ~Matrix5D()
        {
            delete[] m_data;
        }
	
	T get(int i1, int i2, int i3, int i4, int i5)
	{
            return m_data[(i1*m_d2*m_d3*m_d4*m_d5)+(i2*m_d3*m_d4*m_d5)+(i3*m_d4*m_d5)+(i4*m_d5)+i5];
	}
	
	void put(int i1, int i2, int i3, int i4, int i5, T v)
	{
            m_data[(i1*m_d2*m_d3*m_d4*m_d5)+(i2*m_d3*m_d4*m_d5)+(i3*m_d4*m_d5)+(i4*m_d5)+i5] = v;
	}
        
        T* get3DRef(int i1, int i2, int i3)
        {
            return &m_data[(i1*m_d2*m_d3*m_d4*m_d5)+(i2*m_d3*m_d4*m_d5)+(i3*m_d4*m_d5)];
        }
};

#endif