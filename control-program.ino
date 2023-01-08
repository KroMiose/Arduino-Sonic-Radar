#include <SoftwareSerial.h>

#define LED 13

/* 程序配置 */
// 舵机配置
bool servoLog = true;  // 串口输出信息
bool servoRun = true;  // 舵机运行
const int servoPin = 2; // 舵机信号引脚
const byte minlimit = 3;   // 最小角度限制
const byte maxlimit = 177; // 最大角度限制
const int scanspeed = 1;  // 舵机速度

// 超声波测距配置
bool sensorLog = true; // 串口输出信息
const int pingPin = 4; // 超声波模块Trigger引脚
const int echoPin = 5; // 超声波模块Echo引脚

// 蜂鸣器配置
bool enableAlert = true; // 警报开启
int buzzerPin = 11;  // 蜂鸣器信号输出引脚
byte alertCM = 20;  // 报警距离

/* 全局变量设置 */
// 蓝牙模块
SoftwareSerial BTSerial(8, 9); // RX | TX
char tx;

// 舵机模块
//Servo servo;
byte curpos = 90;
byte topos = 0;

void setup() {
  // 初始化
  Serial.begin(9600);
  BTSerial.begin(9600);
  pinMode(servoPin, OUTPUT);
  pinMode(LED,OUTPUT);
  pinMode(buzzerPin,OUTPUT);//设置蜂鸣器引脚输出
  curpos = setServo(servoPin, (maxlimit - minlimit) / 2);
}

void loop() {
  // 舵机模块
  if(servoLog){
    Serial.print("cur pos:");
    Serial.print(curpos);
    Serial.print(" ---- ");
  }
  // 驱动舵机进行范围扫描
  if(servoRun && curpos != topos){
    int setpos = curpos > topos? curpos - scanspeed: curpos + scanspeed;
    curpos = setServo(servoPin, setpos);
  }
  // 舵机位置达到极限时反转目标值
  topos = curpos >= maxlimit? minlimit: (curpos <= minlimit? maxlimit: topos);


  // 超声波测距模块
  long duration, inches, cm;
  pinMode(pingPin, OUTPUT);
  digitalWrite(pingPin, LOW);
  delayMicroseconds(2);
  digitalWrite(pingPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(pingPin, LOW);
  pinMode(echoPin, INPUT);
  duration = pulseIn(echoPin, HIGH);
  inches = microsecondsToInches(duration);
  cm = microsecondsToCentimeters(duration);
  if(sensorLog){  // 打印传感器信息
    Serial.print(inches);
    Serial.print("in, ");
    Serial.print(cm);
    Serial.print("cm");
    Serial.println();
  }

  // 蜂鸣器响应
  if(enableAlert && cm <= alertCM){
    tone(buzzerPin,500,100);
  }

  // 蓝牙通信模块
  String res = "";
  while(BTSerial.available()){
    tx = BTSerial.read();
    res += tx;
  }
  if(res.length() != 0){
    Serial.print("收到来自HC-06: ");
    Serial.println(res);
    
    if(res.equals("ON")){
      digitalWrite(LED,HIGH);
    }
    if(res.equals("OF")){
      digitalWrite(LED,LOW);
    }
  }

  // 信息格式: >角度-距离#
  if(curpos % 3 == 0){
    BTSerial.write(">");
    BTSerial.write(curpos);
    BTSerial.write("-");
    BTSerial.write(cm);
    BTSerial.write("#");
  }
}


/* 功能函数 */
// 测距转换英寸
long microsecondsToInches(long microseconds) {
   return microseconds / 74 / 2;
}

// 测距转换厘米
long microsecondsToCentimeters(long microseconds) {
   return microseconds / 29 / 2;
}

// 设置舵机角度
int setServo(int pin, int angle){
  angle = angle >= maxlimit? maxlimit: angle;
  angle = angle <= minlimit? minlimit: angle;
  for(int i=0;i<50;i++) { //发送50个脉冲
    servopulse(pin, angle); //引用脉冲函数
  }
  return angle;
}

// 脉冲函数
void servopulse(int servopin, int angle){
  int pulsewidth=(angle*11)+500;  //将角度转化为500-2480的脉宽值，每多转1度，对应高电平多11us
  digitalWrite(servopin,HIGH);    //将舵机接口电平至高
  delayMicroseconds(pulsewidth);  //延时脉宽值的微秒数
  digitalWrite(servopin,LOW);     //将舵机接口电平至低
  delayMicroseconds(20000-pulsewidth);   
}
