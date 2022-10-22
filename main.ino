#include "PCM.h"
#include "./output/jrl.h"

//mall 1 and 2 are 2000 sample rate and 2 bits.

//undertale should be the same but I don't remember if that applies to all of them.

//jrl is 2bit and 8000 sample rate

const int SAMPLE_RATE = 8000;
const int BITS = 2; // only 2, 4 or 8 supported

void setup()
{
  startPlayback(defaultSample, sizeof(defaultSample), SAMPLE_RATE, BITS);
  //Serial.begin(9600);

  //Serial.print(bells[0]);
}

void loop()
{
}

