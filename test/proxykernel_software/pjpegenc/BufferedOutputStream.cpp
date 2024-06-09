// 17/12/2013
// This encoder implemented by David Castells-Rufas (david.castells@uab.cat)
// to do research in parallel implementation of the JPEG encoding algorithm
// The code is implemented in C++ and derived from a Java version
//
#include "BufferedOutputStream.h"

BufferedOutputStream::BufferedOutputStream(OutputStream* out)
{
	m_out = out;
	m_size = 0x400 * 4;
	m_buffer = new byte[m_size];
	m_count = 0;
}

BufferedOutputStream::~BufferedOutputStream()
{
	delete [] m_buffer;
}

void BufferedOutputStream::write(int c)
{
	if (m_count < m_size)
	{
		m_buffer[m_count++] = c;
	}
	else
	{
		flush();
		m_buffer[m_count++] = c;
	}
}

void BufferedOutputStream::flush()
{
	m_out->write(m_buffer, 0, m_count);
	m_count = 0;
}

void BufferedOutputStream::write(byte data[], int offset, int len)
{
	if ((m_count + len) < m_size)
	{
		for (int i=0; i < len; i++)
			m_buffer[m_count++] = data[offset+i];
	}
	else
	{
		for (int i=0; i < len; i++)
			write(data[offset+i]);
	}
}
	

void BufferedOutputStream::close()
{
    m_out->close();
}