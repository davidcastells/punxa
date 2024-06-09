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

#include "PerformanceCounter.h"

#include <sys/time.h>

double freq;




void perfCounter(uint64 * p64)
{
    struct timeval time_val;
    gettimeofday(&time_val, 0);

    double secs = (double) time_val.tv_sec;

    secs += ((double) time_val.tv_usec) / 1e6;

    *p64 = (uint64) (secs * 1e6); 
}

double secondsBetweenLaps(uint64 t0, uint64 tf)
{
    uint64 diff = tf - t0;
    
    double secs = diff / 1e6;
    
    return secs;
}