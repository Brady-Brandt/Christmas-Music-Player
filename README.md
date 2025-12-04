# Christmas Music Player

## Requirements
Play a number of Christmas Songs on with a PIC processor using a speaker.
### Inputs:
  - RB0 -> Pause/Play
  - RB1 -> Reset Song
  - RB2 -> Next Song
  - RB4 -> Previous Song
### Outputs:
  - RC0 -> Controls the speaker
  - LCD -> Shows the current song and its time duration
### Interrupts Used:
  - INT0 -> RB0
  - INT1 -> RB1
  - INT2 -> RB2
  - PORTB IOC -> RB4
  - TIMER0 -> Duration of each note
  - TIMER1 -> Frequency of each note
  - TIMER3 -> Keeps track of time
