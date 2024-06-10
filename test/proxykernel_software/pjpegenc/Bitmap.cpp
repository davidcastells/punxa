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
#include "Bitmap.h"

CBitmap::CBitmap() : m_BitmapData(0), m_BitmapSize(0), m_Width(0), m_Height(0) 
{
    Dispose();
}

CBitmap::CBitmap(char* Filename) : m_BitmapData(0), m_BitmapSize(0), m_Width(0), m_Height(0)	
{
    load(Filename);
}

CBitmap::~CBitmap() 
{
    Dispose();
}

bool CBitmap::load(char *Filename)
{
    FILE *file = fopen(Filename, "rb");

    Dispose();

    if (file == 0) 
    {
        printf("ERROR: file not found\n");
        return false;
    }

    fread(&m_BitmapFileHeader, BITMAP_FILEHEADER_SIZE, 1, file);
    if (m_BitmapFileHeader.Signature != BITMAP_SIGNATURE) 
    {
        printf("ERROR: Bad signature %2X != %2X\n", m_BitmapFileHeader.Signature, BITMAP_SIGNATURE);
        return false;
    }

    fread(&m_BitmapHeader, sizeof(BITMAP_HEADER), 1, file);

    if (m_BitmapHeader.BitCount != 24)
    {
        printf("ERROR: bitcount %d\n", m_BitmapHeader.BitCount);
        return false;
    }

    if (m_BitmapHeader.Compression)
            return false;

    m_Width = m_BitmapHeader.Width;
    if (m_Width <0) m_Width = -m_Width;

    m_Height = (m_BitmapHeader.Height < 0)? -m_BitmapHeader.Height: m_BitmapHeader.Height;

    m_BitmapSize = getWidth() * getHeight();
    m_BitmapData = new BGR[m_BitmapSize];

    //fseek(file, BITMAP_FILEHEADER_SIZE + m_BitmapHeader.HeaderSize, SEEK_SET);
    fseek(file, m_BitmapFileHeader.BitsOffset, SEEK_SET);

    fread(m_BitmapData, m_BitmapSize*sizeof(BGR), 1, file);

    fclose(file);
    return true;
}

bool CBitmap::Save(char* Filename)
{
        FILE *file = fopen(Filename, "wb");

        if (file == 0) return false;

        BITMAP_FILEHEADER bfh = {0};
        BITMAP_HEADER bh = {0};

        bh.HeaderSize = sizeof(BITMAP_HEADER);
        bh.BitCount = 24;
        bh.Compression = 0; // RGB
        bh.Planes = 1;
        bh.Height = getHeight();
        bh.Width = getWidth();
        bh.SizeImage = bh.Width * bh.Height * bh.BitCount/8;
        bh.PelsPerMeterX = 3780;
        bh.PelsPerMeterY = 3780;

        bfh.Signature = BITMAP_SIGNATURE;
        bfh.BitsOffset = sizeof(BITMAP_HEADER) + sizeof(BITMAP_FILEHEADER);
        bfh.Size = bh.Width * bh.Height * bh.BitCount/8 + bfh.BitsOffset;

        unsigned char* Bitmap = (unsigned char*) m_BitmapData;

        fwrite(&bfh, sizeof(BITMAP_FILEHEADER), 1, file);
        fwrite(&bh, sizeof(BITMAP_HEADER), 1, file);
        fwrite(Bitmap, bh.SizeImage, 1, file);

        fclose(file);
        return true;
}

bool CBitmap::GetBlock(unsigned x, unsigned y, unsigned sx, unsigned sy, BGR* buf)
{
        //FUNC_ENTER();

        if ((y + sy) > m_Height || (x + sx) > m_Width) {
                //FUNC_EXIT();
                return false;
        }

        for (unsigned r = 0; r < sy; r++)
        {
                unsigned offset = (m_Height - (y+r+1))*m_Width + x;

                for (unsigned c = 0; c < sx; c++)
                {
                        unsigned i = offset + c;
                        buf[sy*r + c] = m_BitmapData[i];
                }
        }

        //FUNC_EXIT();
        return true;
}


bool CBitmap::GetBlock16x16(unsigned x, unsigned y, BGRA buf[16][16])
{
        if ((y + 16) > m_Height || (x + 16) > m_Width) {
                return false;
        }

        for (unsigned r = 0; r < 16; r++)
        {
                unsigned offset = (m_Height - (y+r+1))*m_Width + x;

                for (unsigned c = 0; c < 16; c++)
                {
                        unsigned i = offset + c;

                        buf[r][c].Blue  = m_BitmapData[i].Blue;
                        buf[r][c].Green = m_BitmapData[i].Green;
                        buf[r][c].Red   = m_BitmapData[i].Red;
                        buf[r][c].Alpha = 1;
                }
        }

        return true;
}

bool CBitmap::GetBlock(unsigned x, unsigned y, unsigned sx, unsigned sy, color *R, color *G, color *B)
{
        //FUNC_ENTER();
        if ((y + sy) > m_Height || (x + sx) > m_Width) {
                //FUNC_EXIT();
                return false;
        }

        for (unsigned r = 0; r < sy; r++) {
                unsigned offset = (m_Height - (y+r+1))*m_Width + x;

                for (unsigned c = 0; c < sx; c++) {
                        unsigned i = offset + c;

                        R[sy*r + c] = m_BitmapData[i].Red;
                        G[sy*r + c] = m_BitmapData[i].Green;
                        B[sy*r + c] = m_BitmapData[i].Blue;
                }
        }

        //FUNC_EXIT();
        return true;
}


bool CBitmap::GetBlock16x16(unsigned x, unsigned y, color R[16][16], color G[16][16], color B[16][16])
{
        if ((y + 16) > m_Height || (x + 16) > m_Width) {
                return false;
        }

        for (unsigned r = 0; r < 16; r++)
        {
                unsigned offset = (m_Height - (y+r+1))*m_Width + x;
                unsigned *ptr = (unsigned*)(m_BitmapData + offset);

                // optimization for BGR color format
                for (unsigned c = 0, i = 0; c < 16; c += 4, i += 3)
                {
                        unsigned n1 = ptr[i+0];
                        unsigned n2 = ptr[i+1];
                        unsigned n3 = ptr[i+2];

                        *(unsigned*)&B[r][c] = ((n1 >>  0) & 0xff) | ((n1 >> 16) & 0xff00) | ((n2 >>  0) & 0xff0000) | ((n3 << 16) & 0xff000000);
                        *(unsigned*)&G[r][c] = ((n1 >>  8) & 0xff) | ((n2 <<  8) & 0xff00) | ((n2 >>  8) & 0xff0000) | ((n3 <<  8) & 0xff000000);
                        *(unsigned*)&R[r][c] = ((n1 >> 16) & 0xff) | ((n2 >>  0) & 0xff00) | ((n3 << 16) & 0xff0000) | ((n3 >>  0) & 0xff000000);
                }
        }

        return true;
}


bool CBitmap::SetBlock(unsigned x, unsigned y, unsigned sx, unsigned sy, BGR* buf)
{
        if ((y + sy) > m_Height || (x + sx) > m_Width) {
                return false;
        }

        for (unsigned r = 0; r < sy; r++) {
                unsigned offset = (m_Height - (y+r+1))*m_Width + x;

                for (unsigned c = 0; c < sx; c++) {
                        unsigned i = offset + c;
                        m_BitmapData[i] = buf[sy*r + c];
                }
        }

        return true;
}