#include <pic18.h>
#include "lcd.c"
#include "audio.h"

#define RESET_TIME() minutes = 0; seconds = 0; counter = 0

unsigned short index = 1;
unsigned short note = 0;

unsigned char current_song_index = 0;

const char* current_song_name = 0;
unsigned short current_song_length = 0;
const unsigned short* current_song_clocks = 0;
const unsigned char* current_song_prescalars = 0;
const unsigned short* current_song_notes = 0;
const char* current_song_time = 0;

volatile unsigned char new_song = 1;
volatile unsigned char paused = 0;

unsigned char counter = 0;
unsigned char seconds = 0;
unsigned char minutes = 0;

void interrupt interrupt_handler(){ 
    if(paused){
        TMR0IF = 0;
        TMR1IF = 0;
        TMR3IF = 0;
        goto buttons;
    }

    if (TMR3IF)
    {
        counter++;
        if (counter == 20)
        {
            counter = 0;
            seconds++;
            if (seconds == 60)
            {
                seconds = 0;
                minutes++;
            }
        }
        TMR3 = -62500;
        TMR3IF = 0;
    }

    if(TMR0IF){
       #ifdef TESTING
        //remove this for testing
        if(index == current_song_length){
                RESET_TIME();
                index = 0;
        }
       #else
       if(index == current_song_length){
            current_song_index++;
            if(current_song_index == TOTAL_SONGS) current_song_index = 0;
            current_song_name = SONG_NAMES[current_song_index];
            current_song_length = SONG_LENGTHS[current_song_index];
            current_song_clocks = SONG_CLOCKS[current_song_index];
            current_song_prescalars= SONG_PRESCALARS[current_song_index];
            current_song_notes = SONG_NOTES[current_song_index];
            current_song_time = SONG_TIMES[current_song_index];
            index = 0;
            new_song = 1;

            RESET_TIME(); 
            TMR1IF = 0;
       }
       #endif

       note = current_song_notes[index];
       T0CON = current_song_prescalars[index];
       TMR0 = -current_song_clocks[index++];
       TMR0IF = 0; 
    }
    if(TMR1IF){  
        if(note != REST){
            TMR1 = -note; 
            RC0 ^= 1;
        }
        TMR1IF = 0; 
    }

buttons:
    //pause play
    if(INT0IF){
        paused = !paused;
        INT0IF = 0;
    }

    //play from beginning
    if(INT1IF){
        RESET_TIME();
        index = 0;
        INT1IF = 0;
    }

    //next song
    if(INT2IF){
        current_song_index++;
        if(current_song_index == TOTAL_SONGS) current_song_index = 0;
        current_song_name = SONG_NAMES[current_song_index];
        current_song_length = SONG_LENGTHS[current_song_index];
        current_song_clocks = SONG_CLOCKS[current_song_index];
        current_song_prescalars= SONG_PRESCALARS[current_song_index];
        current_song_notes = SONG_NOTES[current_song_index];
        current_song_time = SONG_TIMES[current_song_index];
        index = 0;
        new_song = 1;
        note = current_song_notes[index];
        T0CON = current_song_prescalars[index];
        TMR0 = -current_song_clocks[index++];
        RESET_TIME();
        INT2IF = 0;
    }

    if(RBIF){
        unsigned char b = PORTB;
        RBIF = 0;
        if(b == 1 << 4){
            //previous song
            if(current_song_index == 0){
                current_song_index = TOTAL_SONGS - 1;
            } else{
                current_song_index--;
            }
            current_song_name = SONG_NAMES[current_song_index];
            current_song_length = SONG_LENGTHS[current_song_index];
            current_song_clocks = SONG_CLOCKS[current_song_index];
            current_song_prescalars= SONG_PRESCALARS[current_song_index];
            current_song_notes = SONG_NOTES[current_song_index];
            current_song_time = SONG_TIMES[current_song_index];
            index = 0;
            new_song = 1;
            note = current_song_notes[index];
            T0CON = current_song_prescalars[index];
            TMR0 = -current_song_clocks[index++];
            RESET_TIME();
        }
    }
}


void write_string(const char* str){
    unsigned char i = 0;
    while(1){
        if(str[i] == 0) break;
        LCD_Write(str[i++]);
    }
}

void main(){
    TRISA = 0;
    TRISB = 0xff;
    TRISC = 0;
    TRISD = 0;
    TRISE = 0;
    ADCON1 = 0x0F;

    RC0 = 1;
    RC1 = 0;

    current_song_name = SONG_NAMES[0];
    current_song_length = SONG_LENGTHS[0];
    current_song_clocks = SONG_CLOCKS[0];
    current_song_prescalars = SONG_PRESCALARS[0];
    current_song_notes = SONG_NOTES[0];
    current_song_time = SONG_TIMES[0];


    T0CS = 0;
    T0CON = current_song_prescalars[0];
    TMR0ON = 1;
    TMR0IE = 1;
    TMR0IP = 1;
    PEIE = 1;

    TMR0 = -current_song_clocks[0];

    T1CON = 0x81;
    TMR1CS = 0;
    TMR1ON = 1;
    TMR1IE = 1;
    TMR1IP = 1;
    PEIE = 1;
    TMR1 = -current_song_notes[0];

    //int0
    INT0IE = 1;
    TRISB0 = 1;

    //int1
    INT1IE = 1; 
    INT1IP = 1;
    TRISB1 = 1;

    //int2
    INT2IE = 1;
    INT2IP = 1;
    TRISB2 = 1;

    LCD_Init();

    
    T3CON = 0xB1;
    TMR3CS = 0;
    TMR3ON = 1;
    TMR3IE = 1;
    TMR3IP = 1;
    TMR3 = -62500;
    PEIE = 1;


    //activate PORTB Interrupt-on-Change
    RBIE = 1;

    GIE = 1;


    unsigned char ones = 0;
    unsigned char temp = 0;

    while (1)
    {
        if (new_song)
        {
            LCD_Inst(0x1);
            LCD_Move(0, 0);
            write_string(current_song_name);
            LCD_Move(1, 2);
            write_string("0:00 / ");
            write_string(current_song_time);
            new_song = 0;
            minutes = 0;
            seconds = 0;
        } else{
            LCD_Move(1,2);
            LCD_Write(minutes + '0');
            LCD_Write(':');
            temp = seconds;
            ones = temp % 10;
            temp /= 10;
            LCD_Write(temp + '0');
            LCD_Write(ones + '0');
        }
    }
}