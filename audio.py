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



mid = mido.MidiFile('elise.mid')


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
            start = active_c2_notes.pop(msg.note)
            duration = current_time - start
            freq = notes[msg.note]
            channel2_data.append((freq, start, duration))

for i, track in enumerate(mid.tracks):
    print(f"Track {i}: {track.name}")
    for msg in track:
        if msg.type == "program_change":
            print(f"  Channel {msg.channel}, Program {msg.program}")

for c in channel1_data:
    print(c)

def remove_chords(channel_data):
    new_data = []
    removed_indicies = []
    for i in range(len(channel_data) - 1):
        if i in removed_indicies:
            continue
        current_data = channel_data[i]

        for j in range(i + 1, len(channel_data)):
            next_note_data = channel_data[j]

            if math.isclose(next_note_data[1], current_data[1]):
                removed_indicies.append(j)
            # if the next note is still playing while the current note is playing
            # skip that note
            elif (next_note_data[1] < current_data[1] + current_data[2]):
                removed_indicies.append(j)
            else:
                break

        new_data.append(current_data)
    return new_data

print(current_time)
new_channel1 = remove_chords(channel1_data)
print(len(channel1_data), len(new_channel1))
new_channel2 = remove_chords(channel2_data)

for i in range(0, 15):
    print(channel1_data[i], new_channel1[i])


with open("audio.h", "w") as f: 
    f.write(f"#define C1_LENGTH {len(new_channel1)}\n")
    f.write(f"const unsigned short c1_clocks[{len(new_channel1)}] = {{")
    max_clocks = 0
    for data in new_channel1:
        clocks = int(data[2] * 10_000_000 / 128)
        if clocks > max_clocks:
            max_clocks = clocks
        if clocks > 65555:
            clocks = 65500
        f.write(f"{clocks},\n") 
    print("Longest Duration: ", max_clocks)
    f.write('};\n')


    f.write(f"const unsigned short c1_notes[{len(new_channel1)}] = {{")
    max_note = 0
    for data in new_channel1:
        if data[0] == 0:
            clocks = 0
        else:
            clocks = int(10000000 / (2 * data[0]))
            if clocks > max_note:
                max_note = clocks
            f.write(f"{clocks},\n") 
    print("Longest note", max_note)
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
 
 