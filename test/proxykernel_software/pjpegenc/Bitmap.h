// 17/12/2013
// This encoder implemented by David Castells-Rufas (david.castells@uab.cat)
// to do research in parallel implementation of the JPEG encoding algorithm
// The code is implemented in C++ and derived from a Java version, see previous
// author licences below
//
/*
 * Windows Bitmap File Loader
 * Version based on 1.2.1 (20070430)
 *
 * Supported Formats: 24 Bit Images
 * Supported compression types: none
 *
 * Created by: Benjamin Kalytta, 2006 - 2007
 * Modified by: Vladimir Antonenko 2009
 * Modified by: David Castells 2013 to support Image like interface
 *
 * Licence: Free to use
 * Source can be found at http://www.kalytta.com/bitmap.h
 */

#include <stdlib.h>
#include <stdio.h>
//#include <memory.h>
#include <string.h>

#include "Image.h"

typedef unsigned char color;

#pragma once
#pragma pack(push)
#pragma pack(1)

#define BITMAP_SIGNATURE ('M'<<8 | 'B')     // 'MB' 

typedef struct __attribute__ ((__packed__)) {
	unsigned short int Signature;
	unsigned int Size;
	unsigned int Reserved;
	unsigned int BitsOffset;
} BITMAP_FILEHEADER;

#define BITMAP_FILEHEADER_SIZE 14

typedef struct __attribute__ ((__packed__)) {
	unsigned int HeaderSize;
	int Width;
	int Height;
	unsigned short int Planes;
	unsigned short int BitCount;
	unsigned int Compression;
	unsigned int SizeImage;
	int PelsPerMeterX;
	int PelsPerMeterY;
	unsigned int ClrUsed;
	unsigned int ClrImportant;
	unsigned int RedMask;
	unsigned int GreenMask;
	unsigned int BlueMask;
	unsigned int AlphaMask;
	unsigned int CsType;
	unsigned int Endpoints[9]; // see http://msdn2.microsoft.com/en-us/library/ms536569.aspx
	unsigned int GammaRed;
	unsigned int GammaGreen;
	unsigned int GammaBlue;
} BITMAP_HEADER;

typedef struct __attribute__ ((__packed__)) {
	color Red;
	color Green;
	color Blue;
	color Alpha;
} RGBA;

typedef struct __attribute__ ((__packed__)) {
	color Blue;
	color Green;
	color Red;
	color Alpha;
} BGRA;

typedef struct __attribute__ ((__packed__)) {
	color Blue;
	color Green;
	color Red;
} BGR;

typedef struct __attribute__ ((__packed__)) {
	unsigned short int Blue:5;
	unsigned short int Green:5;
	unsigned short int Red:5;
	unsigned short int Reserved:1;
} BGR16;

#if 0

#define RIFF_SIGNATURE	0x46464952
#define RIFF_TYPE		0x204c4150
#define PAL_SIGNATURE	0x61746164
#define PAL_UNKNOWN		0x01000300

typedef struct {
	unsigned int Signature;
	unsigned int FileLength;
	unsigned int Type;
	unsigned int PalSignature;
	unsigned int ChunkSize;
	unsigned int Unkown;
} PAL;

#endif

#pragma pack(pop)


class CBitmap : public Image
{
private:
	BITMAP_FILEHEADER m_BitmapFileHeader;
	BITMAP_HEADER m_BitmapHeader;
	BGR *m_BitmapData;
	unsigned int m_BitmapSize;
	unsigned int m_Width;
	unsigned int m_Height;

public:
	
	CBitmap();
	CBitmap(char* Filename);
	virtual ~CBitmap();
	
	void Dispose() {
		if (m_BitmapData) delete[] m_BitmapData;
		m_BitmapData = 0;
		memset(&m_BitmapFileHeader, 0, sizeof(m_BitmapFileHeader));
		memset(&m_BitmapHeader, 0, sizeof(m_BitmapHeader));
		m_Height = m_Width = 0;
	}
	
	/* Load specified Bitmap and stores it as RGBA in an internal buffer */
	
	bool load(char *Filename);
	bool Save(char* Filename);
        
	 int getWidth()  
         {
		return m_Width;
	}
	
	int getHeight()  {
		return m_Height;
	}
	
	unsigned int GetBitCount() const {
		return m_BitmapHeader.BitCount;
	}
	
	unsigned int GetBitmapSize() const {
		return m_BitmapSize;
	}

	BGR* getBytes() {
		return m_BitmapData;
	}

        int getRGB(int x, int y)
        {
		unsigned offset = (m_Height - (y+1))*m_Width + x;

                BGR bgr = m_BitmapData[offset];

                int ARGB = (bgr.Red << 16) | ((bgr.Green << 8)) | ((bgr.Blue));
                return ARGB;

        }

        void getRGB(int x, int y, int* r, int* g, int* b)
        {
            unsigned offset = (m_Height - (y+1))*m_Width + x;

            BGR bgr = m_BitmapData[offset];

            *r = bgr.Red;
            *g = bgr.Green;
            *b = bgr.Blue;
        }

	/* Copies internal RGBA buffer to user specified buffer and convertes into destination bit format.
	 * Supported Bit depths are: 24
	 */
	bool GetBlock(unsigned x, unsigned y, unsigned sx, unsigned sy, BGR* buf);

	bool GetBlock16x16(unsigned x, unsigned y, BGRA buf[16][16]);
	bool GetBlock(unsigned x, unsigned y, unsigned sx, unsigned sy, color *R, color *G, color *B);
	bool GetBlock16x16(unsigned x, unsigned y, color R[16][16], color G[16][16], color B[16][16]);
	bool SetBlock(unsigned x, unsigned y, unsigned sx, unsigned sy, BGR* buf);

};
