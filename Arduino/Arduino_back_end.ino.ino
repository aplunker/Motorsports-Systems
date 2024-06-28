#include<Servo.h>

Servo throttle;
const int fullThrottle = 92;
const int idle = 180;
//analog reads
double throttleIn = 0; 
double thermistor = 0;
double rpm = 0;
double SOC = 0;
double GLV_SOC = 0;

//digital reads
int modeSwitch = 0;
bool gear1 = 0;
bool gear2 = 0;
bool gear3 = 0;

//This will only run once.
void setup() {
  throttle.attach(3);
  throttle.write(map(3.1,1,3.1,idle, fullThrottle));
  Serial.begin(9600); //2400
}

//This will run over and over.
void loop() {

  //Send data to the Serial Port
  throttleIn = analogRead(A1)/203.2 * 1.006; //1016
  // Serial.println(mapf(throttleIn,1,3.1,idle, fullThrottle));
  throttle.write(mapf(throttleIn,1,3.1,idle, fullThrottle)); //signal, min_signal, max_signal, min_angle, max_angle
  thermistor = analogRead(A0)/203.2 * 1.02669;
  SOC = analogRead(A6)/203.2 * 1.006;
  GLV_SOC = analogRead(A4)/67.72;
  modeSwitch = digitalRead(A7);
  gear1 = digitalRead(4);
  gear2 = digitalRead(5);
  gear3 = digitalRead(6);
  if(modeSwitch > 500){
    modeSwitch = 1;
  }else{
    modeSwitch = 0;
  }

  //read rpm - need two pulses - if not getting fast enough skip and say 0.
  bool cont = true;
  short state = 0;
  unsigned long StartTime = millis();
  unsigned long FirstTick = 0; 
  while(cont){
    rpm = analogRead(A5); // for now we say "pulse is anything above 1500"
    if(rpm >= 1500 && state != 1){
      if(state == 0){
        FirstTick = StartTime - millis();
        state++;
      }else{
        cont = false;
        rpm = (60000.0 / ((StartTime - millis()) - FirstTick))*2;
      }
    }else if(rpm < 1500 && state == 1){
      state++;
    }
    if(millis() - StartTime > 300){
      rpm = 0;
      cont = false;
    }

    throttleIn = analogRead(A1)/203.2 * 1.006;
    throttle.write((mapf(throttleIn,1,3.1,idle, fullThrottle))); //signal, min_signal, max_signal, min_angle, max_angle
  }


  Serial.print(throttleIn); 
  Serial.print(",");
  Serial.print(thermistor); 
  Serial.print(",");
  Serial.print(rpm); 
  Serial.print(",");
  Serial.print(SOC); 
  Serial.print(",");
  Serial.print(GLV_SOC); 
  Serial.print(",");
  Serial.println(modeSwitch); 
  // Serial.print(",");
  // Serial.print(gear1); 
  // Serial.print(",");
  // Serial.print(gear2); 
  // Serial.print(",");
  // Serial.println(gear3);
}

int mapf(float x, float in_min, float in_max, int out_min, int out_max)
{
  int value = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
  if(value > out_min){
    value = out_min;
  }else if(value < out_max){
    value = out_max;
  }
  return value;
}