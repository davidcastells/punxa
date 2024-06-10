/**
 * 
 * Copyright (C) 2015, David Castells-Rufas <david.castells@uab.es>, CEPHIS, Universitat Autonoma de Barcelona  
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#ifndef PERFORMANCECOUNTER_H_
#define PERFORMANCECOUNTER_H_


#ifndef INT64_DEFINED
typedef long long int64;
typedef unsigned long long uint64;
#define INT64_DEFINED
#endif

#define PERFORMANCE_COUNTER_FREQ	50000000.0

/**
 * Returns the high performance (64bit) counter value
 * It contains the clock cycles from the system initialization
 *
 * @return the number of clocks (50Mhz) from initialization
 */
/*extern  inline __attribute__((always_inline)) */


void perfCounter(uint64 * p64);

double secondsBetweenLaps(uint64 t0, uint64 tf);

/*
typedef struct _PerformanceCounter
{
	uint64 t0;
	uint64 tf;
} PerformanceCounter;



void PerformanceCounter_PerformanceCounter(PerformanceCounter* this);
void PerformanceCounter_start(PerformanceCounter* this);
void PerformanceCounter_stop(PerformanceCounter* this);
double PerformanceCounter_ellapsedSeconds(PerformanceCounter* this);
*/

#endif /*PERFORMANCECOUNTER_H_*/
