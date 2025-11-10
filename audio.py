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



mid = mido.MidiFile('carolofbells.mid')


ticks_per_beat = mid.ticks_per_beat
tempo = 0

channel1 = 0
channel2 = 0
channels = [0 for i in range(16)]

channel1_data = []
channel2_data = []


c1_time = 0
c2_time = 0

current_time = 0
active_c1_notes = {}
active_c2_notes = {}

merged = mido.merge_tracks(mid.tracks)

for msg in merged:
    if msg.type == 'set_tempo':
        tempo = msg.tempo
    current_time += mido.tick2second(msg.time, ticks_per_beat, tempo)

    if msg.type == 'note_on' and msg.velocity > 0:
        # Start of a note
        if msg.channel == 0 or msg.channel == 12:
            active_c1_notes[msg.note] = current_time
        elif msg.channel == 1 or msg.channel == 13:
            active_c2_notes[msg.note] = current_time

    elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
        if msg.note in active_c1_notes:
            start = active_c1_notes.pop(msg.note)
            duration = current_time - start
            freq = notes[msg.note]
            channel1_data.append((freq, start, duration))
        elif msg.note in active_c2_notes:
            start= active_c2_notes.pop(msg.note)
            duration = current_time - start
            freq = notes[msg.note]
            channel2_data.append((freq, start, duration))

for i, track in enumerate(mid.tracks):
    print(f"Track {i}: {track.name}")
    for msg in track:
        if msg.type == "program_change":
            print(f"  Channel {msg.channel}, Program {msg.program}")





def remove_chords(channel_data):
    new_data = []
    removed_indicies = []
    for i in range(len(channel_data) - 1):
        if i in removed_indicies:
            continue
        current_data = channel_data[i]


        if current_data[2] == 0:
            high_score = 0
        else:
            high_score = current_data[0]
        high_score_index = i 

        if current_data[2] > 1:
            print(current_data)
            continue

        skip_note = False
        for j in range(i + 1, len(channel_data)):
            next_note_data = channel_data[j]

            if current_data[1] + current_data[2] > next_note_data[1] + next_note_data[2]:
                skip_note = True
                break

            if (next_note_data[1] > current_data[1] + current_data[2]) or math.isclose(next_note_data[1], current_data[1] + current_data[2], rel_tol=1e6):
                break

            if next_note_data[2] == 0:
                new_score = 0
            else:
                new_score = next_note_data[0]

            if new_score > high_score:
                high_score = new_score
                high_score_index = j
            
        if skip_note:
            continue
        if high_score_index != i:
            removed_indicies.append(i)
        else:
            new_data.append(channel_data[high_score_index])
    return new_data

print(current_time)
new_channel1 = remove_chords(channel1_data)

for data in new_channel1:
    print(data)

print(len(channel1_data), len(new_channel1))
new_channel2 = remove_chords(channel2_data)


def get_timer0_prescalar(data):
    CLOCK_SPEED = 10_000_000
    UINT16_MAX = 65535
    clock = lambda data, ps: int(data[2] * CLOCK_SPEED / ps)
    if clock(data, 1) < UINT16_MAX:
        return (clock(data, 1), 0x88)
    elif clock(data, 2) < UINT16_MAX:
        return (clock(data, 2), 0x80)
    elif clock(data, 4) < UINT16_MAX:
        return (clock(data, 4), 0x81)
    elif clock(data, 8) < UINT16_MAX:
        return (clock(data, 8), 0x82)
    elif clock(data, 16) < UINT16_MAX:
        return (clock(data, 16), 0x83)
    elif clock(data, 32) < UINT16_MAX:
        return (clock(data, 32), 0x84)
    elif clock(data, 64) < UINT16_MAX:
        return (clock(data, 64), 0x85)
    elif clock(data, 128) < UINT16_MAX:
        return (clock(data, 128), 0x86)
    else:
        return (clock(data, 256), 0x87)

def get_timer1_prescalar(data):
    CLOCK_SPEED = 10_000_000
    UINT16_MAX = 65535
    clock = lambda data, ps: int(CLOCK_SPEED / (2 * data[0] * ps))
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
        f.write(f"{clocks},\n") 
    f.write('};\n')

    f.write(f"const unsigned char c1_prescalars[{len(new_channel1)}] = {{")
    for scalar in prescalars:
        f.write(f"{scalar},\n") 
    f.write('};\n')


    f.write(f"const unsigned short c1_notes[{len(new_channel1)}] = {{")
    max_note = 0
    prescalars = []
    for data in new_channel1:
        if data[0] == 0:
            clocks = 0
        else:
            (clocks, prescalar) = get_timer1_prescalar(data)
            prescalars.append(prescalar)
            f.write(f"{clocks},\n") 
    f.write('};\n')


    f.write(f"const unsigned char c1_notes_scalars[{len(new_channel1)}] = {{")
    for scalar in prescalars:
        f.write(f"{scalar},\n") 
    f.write('};\n')


    f.write(f"#define C2_LENGTH {len(new_channel1)}\n")

    if len(new_channel2) > 0:
        f.write(f"const unsigned short c2_clocks[{len(new_channel2)}] = {{")
        for data in new_channel2:
            clocks = int(data[2] / (100 * 10 ** (-9)))
            f.write(f"{clocks},\n") 
        f.write('};\n')

        f.write(f"const unsigned short c2_notes[{len(new_channel2)}] = {{")
        for data in new_channel2:
            if data[0] == 0:
                clocks = 0
            else:
                if clocks > 65555:
                    print(data)
                clocks = int(10000000 / (2 * data[0]))
            f.write(f"{clocks},\n") 
        f.write('};\n')
 
 