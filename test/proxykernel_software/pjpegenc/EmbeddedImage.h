// 03/07/2015
// This encoder implemented by David Castells-Rufas (david.castells@uab.cat)
// to do research in parallel implementation of the JPEG encoding algorithm
// The code is implemented in C++ and derived from a Java version, see previous
// author licences below
//

#ifndef EMBEDDEDIMAGE_H_INCLUDED_
#define EMBEDDEDIMAGE_H_INCLUDED_

#include "Image.h"

#define GIMP_IMAGE_WIDTH (352)
#define GIMP_IMAGE_HEIGHT (288)
#define GIMP_IMAGE_BYTES_PER_PIXEL (3) /* 3:RGB, 4:RGBA */
#define GIMP_IMAGE_PIXEL_DATA ((unsigned char*) GIMP_IMAGE_pixel_data)

extern const unsigned char GIMP_IMAGE_pixel_data[352 * 288 * 3 + 1];


class EmbeddedImage : public Image
{
private:
    int w;
    int h;
    
public:
    EmbeddedImage()
    {
        w = GIMP_IMAGE_WIDTH;
        h = GIMP_IMAGE_HEIGHT;
    }
    
    virtual int getWidth() 
    {
        return w;
    }
    
    virtual int getHeight() 
    {
        return h;
    }
    
    /**
     * 
     */
    virtual int getRGB(int x, int y)
    {
        unsigned char* pixel = &GIMP_IMAGE_PIXEL_DATA[(y*w+x)*GIMP_IMAGE_BYTES_PER_PIXEL];
        
        int ARGB = pixel[0] << 16 | pixel[1] << 8 | pixel[2];
        
        return ARGB;
    }
    
    /**
     */
     virtual void getRGB(int x, int y, int* r, int* g, int* b)
     {
         unsigned char* pixel = &GIMP_IMAGE_PIXEL_DATA[(y*w+x)*GIMP_IMAGE_BYTES_PER_PIXEL];
        
        *r = pixel[0];
        *g = pixel[1];
        *b = pixel[2];
     }
};

#endif
