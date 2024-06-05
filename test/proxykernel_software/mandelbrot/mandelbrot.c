/**
 *
 * Copyright (C) 2018 David Castells i Rufas (david.castells@uab.cat)
 *
 *	OVERVIEW:
 *	=========
 *	Simple sequential Mandelbrot Set calculation and visualization through
 *	ASCII Art and VGA
 */
#include <math.h>
#include <stdio.h>
#include <time.h>
#include "PerformanceCounter.h"
// #include "vga_controller.h"



#define USE_ASCII_ART
//#define USE_VGA

#ifdef USE_ASCII_ART
	int max_iteration = 100;


	float ymin = -1;
	float ymax = 1;
	float xmin = -2;
	float xmax = 1;

	float divx = 128;
	float divy = 64*2/3;
	int results[128*42];
#endif

#ifdef USE_VGA
	int max_iteration = 255;

	float ymin = -1.125;
	float ymax = 1.125;
	float xmin = -2;
	float xmax = 1;

	float divx = 320;
	float divy = 240;
	unsigned char* results = (int*) (0x80000000 | FRAME_BUFFER_BASE);
#endif


// Lookup table for our ASCII Art
char* lut =   " .-:o*B#";

/**
 *	Print the result nicely
 */
void plot(double x, double y, int color)
{
	static double lasty = -10000;

	if (lasty != y)
		printf("\n");

	color = (int) ((double) color * 256.0 / (double) max_iteration);

	printf("%c", lut[1+color*6/256]);

	lasty = y;

}

void drawPixel(int x, int y, unsigned char rgb8)
{
	int index = y*((int)128)+x ;

	results[index] = rgb8;
}

/**
 *	Stores a computed point of the mandelbrot set in the results array
 *	for later visualization
 */
void putResult(double x0, double y0, int v)
{
	double incx = (xmax-xmin) / divx;
	double incy = (ymax-ymin) / divy;
	int x = ((x0 - xmin) / incx);
	int y = ((y0 - ymin) / incy);


//	printf("put (%d,%d) = %d\n", x, y, v);
//	delay(0.2);

#ifdef USE_VGA
	v = 255 - v;
#endif

	drawPixel(x,y, v);

}

/**
 *	Computes a point of the mandelbrot set
 */
void computePoint(double x0, double y0)
{
	double x = x0; // x co-ordinate of pixel
	double y = y0; // y co-ordinate of pixel

	int iteration = 0;
	int colour;

	while ( (x*x + y*y < (2*2))  &&  (iteration < max_iteration) )
	{
		double xtemp = x*x - y*y + x0;
		double ytemp = 2*x*y + y0;

		x = xtemp;
		y = ytemp;

		iteration = iteration + 1;
	}

	if ( iteration == max_iteration )
		colour = max_iteration;
	else
		colour = iteration;

	putResult(x0, y0, colour);

}

#ifdef USE_VGA

extern vga_controller_dev vga_controller_0;

// Convert from 8 bits
#define BYTETO2BIT(x)	((x>>6)&3)
#define BYTETO3BIT(x)	((x>>5)&7)
#define RGB8(r,g,b)		BYTETO2BIT(r)<<6 | BYTETO3BIT(g)<<3 | BYTETO3BIT(b)

void testVideo()
{
	dev = &vga_controller_0;
	printf("VGA DEV = %08X.\n", dev);

	unsigned char* fb = (unsigned char*)(0x80000000 | FRAME_BUFFER_BASE);

	for (int y=0; y < 320; y++)
		for (int x=0; x < 320; x++)
		{
			int pos =y*320+x;
			fb[pos] = RGB8(0,0,255);
		}

	vga_set(dev, 0, 4);

	delay(1);
}
#endif

/**
 *	Mandelbrot set computation
 */
int main()
{
	uint64 t0, tf;

#ifdef USE_VGA
	testVideo();
#endif

	//t0 = perfCounter();
	double x;
	double y;

	printf("Generating a mandelbrot set %dx%d (%d iterations)",  (int) divx, (int) divy, max_iteration);

	for (y=ymin; y<=ymax; y+= (ymax-ymin)/divy)
	{
		double incy = (ymax-ymin) / divy;
		int iy = ((y - ymin) / incy);

		printf("compute line %d\n", iy);

		for (x=xmin; x<=xmax; x+= (xmax-xmin)/divx)
			computePoint(x, y);
	}

	//tf = perfCounter();
	int iy,ix;

#ifdef USE_ASCII_ART
	for (iy=0; iy < 42; iy++)
		for (ix=0; ix < 128; ix++)
			plot(ix, iy, results[iy*128+ix]);

	printf("\n");
#endif

	//printLap(t0, tf);
}

