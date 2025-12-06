from collections import Counter

import mido
import os

class Song:
    def __init__(self, file_name: str, name: str, channel: int, 
                 time_correction = 0, add_rests = True, fix_overlap = False, rest_tol = 1000, secondary_channels = [],
                   overlap_tolerance = 0):
        self.file_path = "songs" + os.path.sep + file_name
        self.name = name 
        self.channel = channel
        self.file_name = file_name.replace(".mid", "")
        self.add_rests = add_rests
        self.fix_overlap = fix_overlap 
        self.rest_tolerance = rest_tol
        self.secondary_channels = secondary_channels
        self.overlap_tolerance = overlap_tolerance
        self.time_correction = time_correction

class AudioData:
    ticks_per_beat = 0
    def __init__(self, freq: float, start: int, duration: int, velocity: int, tempo: int):
        self.freq = freq
        self.start = start # start time in ticks
        self.duration = duration  # duration in ticks
        self.velocity = velocity 
        self.time_duration = (tempo * duration * 10) / (AudioData.ticks_per_beat) #number of pic clocks
        self.tempo = tempo

    def update_duration(self, duration: int):
        self.duration = duration
        self.time_duration = (self.tempo * duration * 10) / (AudioData.ticks_per_beat) #number of pic clocks

    def __str__(self):
       return f"freq: {self.freq}, start: {self.start}, duration: {self.duration}, time: {self.time_duration}" 
 
REST_FREQ = 40_000
REST = 10_000_000 / (REST_FREQ * 2)

TESTING = False

songs = []


songs.append(Song("carolofbells.mid", "Carol of Bells", 0, add_rests=False, overlap_tolerance=1))
songs.append(Song("deck.mid", "Deck the Halls", 2, time_correction=-1))
songs.append(Song("hollyjolly.mid", "Holly Jolly Xmas", 6, time_correction=-3, rest_tol=20, secondary_channels=[5]))
songs.append(Song("jinglebells.mid", "Jingle Bells", 0, time_correction=-1))
songs.append(Song("herecomes.mid", "Here Comes Santa", 0, rest_tol=80, time_correction=-1))
songs.append(Song("letitsnow.mid", "Let it snow", 5, rest_tol=50, time_correction=6))
songs.append(Song("bellrock.mid", "Jingle Bell Rock", 3, rest_tol=40))
songs.append(Song("rudolph.mid", "Rudolph", 0, fix_overlap=True, time_correction=3))
songs.append(Song("frosty.mid", "Frosty", 1, time_correction=4))
songs.append(Song("Allwantisyou.mid", "All I want for Xmas is you", 3, add_rests=False, time_correction=6))
songs.append(Song("wishyou.mid", "Wish merry Xmas", 2, rest_tol=120))
songs.append(Song("twelvedays.mid", "12 Days of Xmas", 6, time_correction=-7))
songs.append(Song("sleighride.mid", "Sleigh Ride", 2))


notes = [
8.18, 8.66, 9.18, 9.72, 10.30, 10.91, 11.56, 12.25, 12.98, 13.75,
14.57, 15.43, 16.35, 17.32, 18.35, 19.45, 20.60, 21.83, 23.12, 24.50,
25.96, 27.50, 29.14, 30.87, 32.70, 34.65, 36.71, 38.89, 41.20, 43.65, 
46.25, 49.00, 51.91, 55.00, 58.27, 61.74, 65.41, 69.30, 73.42, 77.78, 
82.41, 87.31, 92.50, 98.00, 103.83, 110.00, 116.54, 123.47, 130.81, 138.59,
146.83, 155.56, 164.81, 174.61, 185.00, 196.00, 207.65, 220.00, 233.08, 246.94,
261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392.00, 415.30, 440.00,
466.16, 493.88, 523.25, 554.37, 587.33, 622.25, 659.26, 698.46, 739.99, 783.99,
830.61, 880.00, 932.33, 987.77, 1046.50, 1108.73, 1174.66, 1244.51, 1318.51, 1396.91, 
1479.98, 1567.98, 1661.22, 1760.00, 1864.66, 1975.53, 2093.00, 2217.46, 2349.32, 2489.02, 
2637.02, 2793.83, 2959.96, 3135.96, 3322.44, 3520.00, 3729.31, 3951.07, 4186.01, 4434.92,
4698.64, 4978.03, 5274.04, 5587.65, 5919.91, 6271.93, 6644.88, 7040.00, 7458.62, 7902.13,
8372.02, 8869.84, 9397.27, 9956.06, 10548.08, 11175.30, 11839.82, 12543.85 
]



def get_audio_data(current_song: Song) -> list[AudioData]:
    print(f"Getting Audio data for {current_song.name} from file: {current_song.file_path}")

    mid = mido.MidiFile(current_song.file_path)
    ticks_per_beat = mid.ticks_per_beat
    AudioData.ticks_per_beat = ticks_per_beat

    #useful for seeing which instruments are on which channels
    if TESTING: 
        for i, track in enumerate(mid.tracks):
            print(f"Track {i}: {track.name}")
            for msg in track:
                if msg.type == "program_change":
                    print(f"  Channel {msg.channel}, Program {msg.program}")

    
    tempo = 0

    channel_data = []

    active_c1_notes = {}

    merged = mido.merge_tracks(mid.tracks)

    # used to show how many notes are played on each channel
    channels = [0 for i in range(16)]

    current_time = 0 # current time in seconds
    current_ticks = 0 #current time in ticks for more accurate timing

    for msg in merged:
        current_time += mido.tick2second(msg.time, ticks_per_beat, tempo)
        current_ticks += msg.time

        if msg.type == 'set_tempo':
            tempo = msg.tempo

        if msg.type == "note_on":
            channels[msg.channel] += 1

        if msg.type == 'note_on' and msg.velocity > 0:
            # Start of a note
            if msg.channel == current_song.channel or msg.channel in current_song.secondary_channels:
                active_c1_notes[msg.note] = (current_ticks, msg.velocity)

        elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
            if msg.note in active_c1_notes:
                (start, velocity) = active_c1_notes.pop(msg.note)
                duration = current_ticks - start
                freq = notes[msg.note]
                channel_data.append(AudioData(freq, start, duration, velocity, tempo)) 

    # ensure the data is in the correct order
    channel_data.sort(key= lambda d: d.start)
    print("Channel Info:", channels)
    print(f"Song Length: {int(current_time)} seconds")
    return channel_data


def remove_chords(song: Song, channel_data: list[AudioData]) -> list[AudioData]:
    melody = []

    for note in channel_data:
        freq = note.freq
        start = note.start
        duration = note.duration
        velocity = note.velocity
        end = start + duration

        tick_tolerance = 5
        rest_tolerance = song.rest_tolerance

        if not melody:
            melody.append(note)
            continue

        prev_freq = melody[-1].freq
        prev_start = melody[-1].start
        prev_velocity = melody[-1].velocity
        prev_end = prev_start + melody[-1].duration

        # notes don't overlap
        if start >= prev_end + song.overlap_tolerance:
            # handle rests
            if start - prev_end > tick_tolerance and song.add_rests:
                tempo = note.tempo
                diff = start - prev_end
                # try to mimic natural fade
                if diff > rest_tolerance:
                    melody[-1].update_duration(melody[-1].duration + diff - rest_tolerance)
                    melody.append(AudioData(REST_FREQ, 0,duration=rest_tolerance,velocity=0,tempo=tempo))
                else:
                    melody.append(AudioData(REST_FREQ, 0,duration=diff,velocity=0,tempo=tempo))
            melody.append(note)
            continue

        # songs like rudolph have overlapping notes for some reason
        # despite the fact its played on a saxophone so I try to fix it here
        if song.fix_overlap and prev_end > start:
            melody[-1].update_duration(melody[-1].duration - (prev_end - start))
            note.update_duration((note.duration + (start - prev_end)))
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

        # some notes appear to overlap even though they don't
        if start - tick_tolerance <= prev_end:
            melody.append(note)
            continue


    return melody 

def get_time(time_seconds: float) -> str: 
    seconds = round(time_seconds)
    minutes = seconds // 60
    seconds = seconds % 60
    print(time_seconds, f"{minutes}:{seconds:02}")

    return f"{minutes}:{seconds:02}" 


def get_timer0_prescalar(data):
    UINT16_MAX = 65535
    if data.time_duration < UINT16_MAX:
        return (data.time_duration, 1,0x88)
    elif data.time_duration // 2 < UINT16_MAX:
        return (data.time_duration // 2, 2,0x80)
    elif data.time_duration // 4 < UINT16_MAX:
        return (data.time_duration // 4, 4,0x81)
    elif data.time_duration // 8 < UINT16_MAX:
        return (data.time_duration // 8, 8,0x82)
    elif data.time_duration // 16 < UINT16_MAX:
        return (data.time_duration // 16, 16,0x83)
    elif data.time_duration // 32 < UINT16_MAX:
        return (data.time_duration // 32, 32,0x84)
    elif data.time_duration // 64 < UINT16_MAX:
        return (data.time_duration // 64, 64,0x85)
    elif data.time_duration // 128 < UINT16_MAX:
        return (data.time_duration // 128, 128,0x86)
    else:
        return (data.time_duration // 256, 256, 0x87)

def output_audio_data(file, song: Song, audio_data: list[AudioData]) -> float:
    file.write(f"const unsigned short {song.file_name}_clocks[{len(audio_data)}] = {{")
    prescalars = []

    CLOCK_SPEED = 10_000_000

    time_seconds = 0
    for data in audio_data:
        (clocks, scalar, prescalar) = get_timer0_prescalar(data)
        clocks = int(clocks) 
 
        # could insert another note instead of clamping
        # but the songs sound just fine as is
        if clocks > 65535:
            clocks = 65535
        
        time_seconds += (clocks * scalar) / CLOCK_SPEED 
        prescalars.append(prescalar)
        file.write(f"{int(clocks)},\n") 
    file.write('};\n')

    time_seconds += song.time_correction

    print(f"Duration Prescalars: {Counter(prescalars)}")

    file.write(f"const unsigned char {song.file_name}_prescalars[{len(audio_data)}] = {{")
    for scalar in prescalars:
        file.write(f"{scalar},\n") 
    file.write('};\n')


    file.write(f"const unsigned short {song.file_name}_notes[{len(audio_data)}] = {{")
    for data in audio_data:
        clocks = int(CLOCK_SPEED / (2 * data.freq))
        file.write(f"{clocks},\n") 
    file.write('};\n')
    return time_seconds


#main
with open("audio.h", 'w') as f:
    times = []
    audio_data_lengths = []
    f.write(f"#define REST {int(REST)}\n")
    f.write(f"#define TOTAL_SONGS {len(songs)}\n")
    f.write("const char* SONG_NAMES[] = {\n")
    for song in songs:
        f.write(f"\"{song.name}\",")
    f.write("};\n")

    songs_cnt = len(songs)
    if TESTING:
        songs_cnt = 1


    for i in range(songs_cnt):
        song = songs[i]
        audio_data = get_audio_data(song)
        cleaned_audio_data = remove_chords(song, audio_data)
        audio_data_lengths.append(len(cleaned_audio_data))
        print(len(audio_data), len(cleaned_audio_data))
        time_seconds = output_audio_data(f, song, cleaned_audio_data)
        times.append(get_time(time_seconds))

    if TESTING:
        f.write("#define TESTING 1\n")
        songs = [songs[0]]

    f.write("unsigned short SONG_LENGTHS[] = {")
    for i in range(0, len(audio_data_lengths)):
        f.write(f"{audio_data_lengths[i]},") 
    f.write("};\n")

    f.write("const char* SONG_TIMES[] = {")
    for time in times:
        f.write(f"\"{time}\",")
    f.write("};\n")


    f.write("const unsigned short* SONG_CLOCKS[] = {")
    for song in songs:
        f.write(f"{song.file_name}_clocks,") 
    f.write("};\n")

    f.write("const unsigned char* SONG_PRESCALARS[] = {")
    for song in songs:
        f.write(f"{song.file_name}_prescalars,") 
    f.write("};\n")

    f.write("const unsigned short* SONG_NOTES[] = {")
    for song in songs:
        f.write(f"{song.file_name}_notes,") 
    f.write("};\n")