#include "PCM.h"
#include "./output/computer.h"

//computer.h is an example pcm file.

const int SAMPLE_RATE = 10000; // 10 000 sample rate generally isn't recommended for memory efficiency. 2bit, 4k or 8k have produced comparable results.
const int BITS = 2; // only 1, 2, 4 or 8 supported

void setup()
{

}

void loop()
{
  startPlayback(defaultSample, sizeof(defaultSample), SAMPLE_RATE, BITS);

  delay( (( (sizeof(defaultSample) / sizeof(defaultSample[0])) * (8 / BITS) ) / SAMPLE_RATE) * 1000 ); // FORMULA IS BROKEN

  stopPlayback();
}

