import mido
import math


notes = [
8.18, 8.66, 9.18, 9.72, 10.30, 10.91, 11.56, 12.25,
12.98, 13.75, 14.57, 15.43, 16.35, 17.32, 18.35,
19.45, 20.60, 21.83, 23.12, 24.50, 25.96, 27.50,
29.14, 30.87, 32.70, 34.65, 36.71, 38.89, 41.20,
43.65, 46.25, 49.00, 51.91, 55.00, 58.27, 61.74, 
65.41, 69.30, 73.42, 77.78, 82.41, 87.31, 92.50, 
98.00, 103.83, 110.00, 116.54, 123.47, 130.81, 
138.59, 146.83, 155.56, 164.81,
174.61,
185.00,
196.00,
207.65,
220.00,
233.08,
246.94,
261.63,
277.18,
293.66,
311.13,
329.63,
349.23,
369.99,
392.00,
415.30,
440.00,
466.16,
493.88,
523.25,
554.37,
587.33,
622.25,
659.26,
698.46,
739.99,
783.99,
830.61,
880.00,
932.33,
987.77,
1046.50,
1108.73,
1174.66,
1244.51,
1318.51,
1396.91,
1479.98,
1567.98,
1661.22,
1760.00,
1864.66,
1975.53,
2093.00,
2217.46,
2349.32,
2489.02,
2637.02,
2793.83,
2959.96,
3135.96,
3322.44,
3520.00,
3729.31,
3951.07,
4186.01,
4434.92,
4698.64,
4978.03,
5274.04,
5587.65,
5919.91,
6271.93,
6644.88,
7040.00,
7458.62,
7902.13,
8372.02,
8869.84,
9397.27,
9956.06,
10548.08,
11175.30,
11839.82,
12543.85
]



mid = mido.MidiFile('alla-turca.mid')


ticks_per_beat = mid.ticks_per_beat
tempo = 0

channel1 = 0
channels = [0 for i in range(16)]

channel1_data = []

class AudioData:
    def __init__(self, freq: float, start: int, duration: int, velocity: int, time_duration: float):
        self.freq = freq
        self.start = start 
        self.duration = duration 
        self.velocity = velocity 
        self.time_duration = time_duration
    def __str__(self):
       return f"freq: {self.freq}, start: {self.start}, duration: {self.duration}, vel: {self.velocity}" 
        

c1_time = 0

current_time = 0
active_c1_notes = {}

merged = mido.merge_tracks(mid.tracks)

current_ticks = 0

for msg in merged:
    current_time += mido.tick2second(msg.time, ticks_per_beat, tempo)
    current_ticks += msg.time

    if msg.type == 'set_tempo':
        tempo = msg.tempo


    if msg.type == 'note_on' and msg.velocity > 0:
        # Start of a note
        if msg.channel == 0 or msg.channel == 12:
            active_c1_notes[msg.note] = (current_ticks, msg.velocity)

    elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
        if msg.note in active_c1_notes:
            (start, velocity) = active_c1_notes.pop(msg.note)
            duration = current_ticks - start
            freq = notes[msg.note]
            channel1_data.append(AudioData(freq, start, duration, velocity, (tempo * duration * 10) / (ticks_per_beat))) 

for i, track in enumerate(mid.tracks):
    print(f"Track {i}: {track.name}")
    for msg in track:
        if msg.type == "program_change":
            print(f"  Channel {msg.channel}, Program {msg.program}")


def remove_chords(channel_data, time_tolerance=0.05):
    melody = []

    for note in channel_data:
        freq = note.freq
        start = note.start
        duration = note.duration
        velocity = note.velocity
        end = start + duration

        tick_tolerance = 5

        if not melody:
            melody.append(note)
            continue

        prev_freq = melody[-1].freq
        prev_start = melody[-1].start
        prev_velocity = melody[-1].velocity
        prev_end = prev_start + melody[-1].duration



        # notes don't overlap
        if start > prev_end:
            melody.append(note)
            continue

        # only play one note in a chord
        if start == prev_start:
            if melody[-1].duration == duration:
                if freq > prev_freq:
                    melody[-1] = note
            elif melody[-1].duration > duration:
                melody[-1] = note
            continue


        if start - tick_tolerance <= prev_end:
            melody.append(note)
            continue

    return melody    


print(f"Song Length: {int(current_time)} seconds")
new_channel1 = remove_chords(channel1_data, 1e-6)

for i in range(50):
    print(channel1_data[i], new_channel1[i])

print(len(channel1_data), len(new_channel1))


def get_timer0_prescalar(data):
    CLOCK_SPEED = 10_000_000
    UINT16_MAX = 65535
    clock = lambda data, ps: int(data.time_duration * CLOCK_SPEED / ps)
    if data.time_duration < UINT16_MAX:
        return (data.time_duration, 0x88)
    elif data.time_duration / 2 < UINT16_MAX:
        return (data.time_duration / 2, 0x80)
    elif data.time_duration / 4 < UINT16_MAX:
        return (data.time_duration / 4, 0x81)
    elif data.time_duration / 8 < UINT16_MAX:
        return (data.time_duration / 8, 0x82)
    elif data.time_duration / 16 < UINT16_MAX:
        return (data.time_duration / 16, 0x83)
    elif data.time_duration / 32 < UINT16_MAX:
        return (data.time_duration / 32, 0x84)
    elif data.time_duration / 64 < UINT16_MAX:
        return (data.time_duration / 64, 0x85)
    elif data.time_duration / 128 < UINT16_MAX:
        return (data.time_duration / 128, 0x86)
    else:
        return (data.time_duration / 256, 0x87)

def get_timer1_prescalar(data):
    CLOCK_SPEED = 10_000_000
    UINT16_MAX = 65535
    clock = lambda data, ps: int(CLOCK_SPEED / (2 * data.freq * ps))
    if clock(data, 1) < UINT16_MAX:
        return (clock(data, 1), 0x81)
    elif clock(data, 2) < UINT16_MAX:
        return (clock(data, 2), 0x91)
    elif clock(data, 4) < UINT16_MAX:
        return (clock(data, 4), 0xA1)
    else:
        return (clock(data, 8), 0xB1)



with open("audio.h", "w") as f: 
    f.write(f"#define C1_LENGTH {len(new_channel1)}\n")
    f.write(f"const unsigned short c1_clocks[{len(new_channel1)}] = {{")
    prescalars = []
    for data in new_channel1:
        (clocks, prescalar) = get_timer0_prescalar(data)
        prescalars.append(prescalar)
        f.write(f"{int(clocks)},\n") 
    f.write('};\n')

    f.write(f"const unsigned char c1_prescalars[{len(new_channel1)}] = {{")
    for scalar in prescalars:
        f.write(f"{scalar},\n") 
    f.write('};\n')


    f.write(f"const unsigned short c1_notes[{len(new_channel1)}] = {{")
    max_note = 0
    prescalars = []
    for data in new_channel1:
        (clocks, prescalar) = get_timer1_prescalar(data)
        prescalars.append(prescalar)
        f.write(f"{clocks},\n") 
    f.write('};\n')


    f.write(f"const unsigned char c1_notes_scalars[{len(new_channel1)}] = {{")
    for scalar in prescalars:
        f.write(f"{scalar},\n") 
    f.write('};\n') 