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

## Hardware and Software
### Flowchart
![Flowchart](https://github.com/Brady-Brandt/Christmas-Music-Player/blob/main/flowchart.jpg)
### Code:
[C Code](https://github.com/Brady-Brandt/Christmas-Music-Player/blob/main/player.c)

I also used Python to parse midi files (a special format digital synthesizers use) to create the actual music.
This made it way quicker and easier for me to add new songs. I parse the files in Python and generate C code (audio.h)
that gets included with the rest of the project.

[Python Code](https://github.com/Brady-Brandt/Christmas-Music-Player/blob/main/audio.py)

## Song List
- Carol of the Bells
- Deck the Halls
- Holly Jolly Christmas
- Jingle Bells
- Here Comes Santa Claus
- Let it Snow
- Jingle Bell Rock
- Rudolph
- Frosty the Snowman
- All I want for Christmas is you
- We Wish you a Merry Christmas
- 12 Days of Christmas
- Sleigh Ride
