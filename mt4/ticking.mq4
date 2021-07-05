//+------------------------------------------------------------------+
//|                                                        PiAir.mq4 |
//|                        Copyright 2017, MetaQuotes Software Corp. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2017, MetaQuotes Software Corp."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict
//#include <hash.mqh>
//--- input parameters
#include <Arrays\ArrayObj.mqh>
string DATA_PATH="data\\";
string FILENAME="_Tick.csv";
string TICK_TRIGGER = DATA_PATH+"ticking_trigger.txt";
datetime LastActionTime = 0;
int     prevSecondTime  = 0;
uint    prevSecondTick  = 0;
MqlTick TICKS[];

class CTick : public CObject{
   public: 
      string tickTime;
      string symbol;
      double tickPrice;
      int volume;
      
   CTick(const string time,const string sym, const double price,const int vol):
      tickTime(time), symbol(sym), tickPrice(price), volume(vol){}
};
CArrayObj *listOfTicks;
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit(){
   listOfTicks=new CArrayObj();
   return(INIT_SUCCEEDED);
}
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick(){
   // put tick to memory
   MqlTick last_tick;
   if(SymbolInfoTick(Symbol(),last_tick)){
      //string time = TimeLocal() + "." + getCurrentMs();
      string time = TimeGMT() + "." + getCurrentMs();
      string symbol = Symbol();
      double price  = (last_tick.ask + last_tick.bid) / 2.0;
      int volume    = last_tick.volume;
      listOfTicks.Add(new CTick(time,symbol,price,volume));
   }
   
   // Comparing LastActionTime with the current starting time for the candle.
   if (LastActionTime != Time[0]){
      if (FileIsExist(TICK_TRIGGER)){
         // Code to execute once per bar.
         // define output file name
         string timeString = TimeToStr(LastActionTime);
         StringReplace(timeString,":","_");
         StringReplace(timeString," ","_");
         string filename = DATA_PATH+Symbol()+"_"+ timeString + FILENAME;
         
         // write to file
         int handle=FileOpen(filename,FILE_WRITE|FILE_CSV,',');
         if(handle>0){
            FileWrite(handle,"TickTime","Symbol","Price","Volume");
            for(int i=0;i<listOfTicks.Total();i++){
               CTick *oneTick = listOfTicks.At(i);
               FileWrite(handle,oneTick.tickTime,oneTick.symbol,oneTick.tickPrice,oneTick.volume);
            }
            FileFlush(handle);
            FileClose(handle);
         }
      }
      listOfTicks.Clear();
      LastActionTime = Time[0];
   }
}
//+------------------------------------------------------------------+
void OnDeinit(const int reason){
   delete listOfTicks;
}
//+------------------------------------------------------------------+
int getCurrentMs() {
    return(GetTickCount() - prevSecondTick);
}
//+------------------------------------------------------------------+
void OnTimer() {
    //If a new "second" occurs, record down the GetTickCount()
    if(TimeLocal() > prevSecondTime) {
        prevSecondTick  = GetTickCount();
        prevSecondTime  = TimeLocal();
    }
}
