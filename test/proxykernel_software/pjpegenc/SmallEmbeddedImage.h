// 03/07/2015
// This encoder implemented by David Castells-Rufas (david.castells@uab.cat)
// to do research in parallel implementation of the JPEG encoding algorithm
// The code is implemented in C++ and derived from a Java version, see previous
// author licences below
//

#ifndef SMALL_EMBEDDEDIMAGE_H_INCLUDED_
#define SMALL_EMBEDDEDIMAGE_H_INCLUDED_

#include "Image.h"

#define GIMP_IMAGE_WIDTH (32)
#define GIMP_IMAGE_HEIGHT (32)
#define GIMP_IMAGE_BYTES_PER_PIXEL (3) 



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
    
    virtual int getRGB(int x, int y);
    virtual void getRGB(int x, int y, int* r, int* g, int* b);

};

#endif
