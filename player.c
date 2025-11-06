#include <pic18.h>
#include "audio.h"


#define USHORT_MAX 65535


volatile unsigned short index = 1;
volatile unsigned short note = 0;



void interrupt interrupt_handler(){ 
    if(TMR0IF){
       note = c1_notes[index];
       TMR0 = -c1_clocks[index++];
       if(index == C1_LENGTH) index = 0;
       TMR0IF = 0; 
    }
    if(TMR1IF){ 
        TMR1 = -note; 
        RC0 = !RC0;
        TMR1IF = 0; 
    }
}



void main(){
   TRISA = 0;
   TRISB = 0;
   TRISC = 0;
   TRISD = 0;
   TRISE = 0;
   ADCON1 = 0x0F;

    /*
    PR2 = A_TIMER2; 
    T2CON = (B_TIMER2 << 3) | C_TIMER2;
    TMR2IE = 1;
    TMR2ON = 1;
    TMR2IP = 1;
    */

    T0CS = 0;
    T0CON = 0x86;
    TMR0ON = 1;
    TMR0IE = 1;
    TMR0IP = 1;
    PEIE = 1;

    TMR0 = -c1_clocks[0];

    T1CON = 0x81;
    TMR1CS = 0;
    TMR1ON = 1;
    TMR1IE = 1;
    TMR1IP = 1;
    PEIE = 1;
    TMR1 = -c1_notes[0];

    /*
    T3CON = 0x81;
    TMR3CS = 0;
    TMR3ON = 1;
    TMR3IE = 1;
    TMR3IP = 1;
    PEIE = 1;
    */


    GIE = 1;

    while(1);
}