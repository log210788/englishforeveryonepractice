#!/usr/bin/env python3
"""
Generates a 32-second peaceful, lush Studio Ghibli inspired acoustic piano & ambient string loop.
Saved as e:\class aids\code\englishForEveryoneOne\audio\ghibli_bg_music.wav
"""

import math
import struct
import wave
import os

SAMPLE_RATE = 44100
DURATION = 32.0  # seconds
NUM_SAMPLES = int(SAMPLE_RATE * DURATION)

def note_to_freq(note_name):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = int(note_name[-1])
    key = note_name[:-1]
    idx = notes.index(key)
    # A4 = 440 Hz (idx 9, octave 4)
    semitones = (octave - 4) * 12 + (idx - 9)
    return 440.0 * (2.0 ** (semitones / 12.0))

# Ghibli-esque Melodic Song Structure (32 seconds = 8 bars at 60 BPM)
# Bar 1: Fmaj7 | Bar 2: Cmaj7 | Bar 3: Dm7 | Bar 4: Am7
# Bar 5: Bbmaj7 | Bar 6: F/A | Bar 7: Gm7 | Bar 8: Csus4 -> C7

melody_timeline = [
  # Bar 1 (0.0s - 4.0s)
  (0.0, 'F3', 3.5, 0.4), (0.0, 'C4', 3.0, 0.3), (0.0, 'E4', 3.0, 0.35), (0.0, 'A4', 3.0, 0.35),
  (0.8, 'C5', 1.2, 0.4), (2.0, 'E5', 1.8, 0.45), (3.2, 'G5', 1.2, 0.4),

  # Bar 2 (4.0s - 8.0s)
  (4.0, 'C3', 3.5, 0.4), (4.0, 'G3', 3.0, 0.3), (4.0, 'B3', 3.0, 0.35), (4.0, 'E4', 3.0, 0.35),
  (4.8, 'G4', 1.2, 0.4), (6.0, 'C5', 1.8, 0.45), (7.2, 'E5', 1.2, 0.4),

  # Bar 3 (8.0s - 12.0s)
  (8.0, 'D3', 3.5, 0.4), (8.0, 'F3', 3.0, 0.3), (8.0, 'A3', 3.0, 0.35), (8.0, 'C4', 3.0, 0.35),
  (8.8, 'F4', 1.2, 0.4), (10.0, 'A4', 1.8, 0.45), (11.2, 'D5', 1.2, 0.4),

  # Bar 4 (12.0s - 16.0s)
  (12.0, 'A2', 3.5, 0.4), (12.0, 'E3', 3.0, 0.3), (12.0, 'G3', 3.0, 0.35), (12.0, 'C4', 3.0, 0.35),
  (12.8, 'E4', 1.2, 0.4), (14.0, 'G4', 1.8, 0.45), (15.2, 'C5', 1.2, 0.4),

  # Bar 5 (16.0s - 20.0s)
  (16.0, 'A#2', 3.5, 0.4), (16.0, 'F3', 3.0, 0.3), (16.0, 'A3', 3.0, 0.35), (16.0, 'D4', 3.0, 0.35),
  (16.8, 'F4', 1.2, 0.4), (18.0, 'A4', 1.8, 0.45), (19.2, 'D5', 1.2, 0.4),

  # Bar 6 (20.0s - 24.0s)
  (20.0, 'F3', 3.5, 0.4), (20.0, 'A3', 3.0, 0.3), (20.0, 'C4', 3.0, 0.35), (20.0, 'F4', 3.0, 0.35),
  (20.8, 'C5', 1.2, 0.4), (22.0, 'A4', 1.8, 0.45), (23.2, 'F4', 1.2, 0.4),

  # Bar 7 (24.0s - 28.0s)
  (24.0, 'G2', 3.5, 0.4), (24.0, 'D3', 3.0, 0.3), (24.0, 'A#3', 3.0, 0.35), (24.0, 'D4', 3.0, 0.35),
  (24.8, 'F4', 1.2, 0.4), (26.0, 'A#4', 1.8, 0.45), (27.2, 'D5', 1.2, 0.4),

  # Bar 8 (28.0s - 32.0s)
  (28.0, 'C3', 3.5, 0.4), (28.0, 'G3', 3.0, 0.3), (28.0, 'C4', 3.0, 0.35), (28.0, 'E4', 3.0, 0.35),
  (28.8, 'G4', 1.2, 0.4), (30.0, 'C5', 1.8, 0.45), (31.2, 'E5', 1.2, 0.4)
]

def synthesize_piano_note(freq, duration, velocity):
    num_samples = int(SAMPLE_RATE * duration)
    buffer = [0.0] * num_samples
    
    # Harmonics: fundamental, 2nd, 3rd, 4th, 5th
    harmonics = [(1.0, 1.0), (2.0, 0.45), (3.0, 0.2), (4.0, 0.1), (5.0, 0.05)]
    
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        
        # Exponential Piano Envelope (quick attack, gentle decay)
        attack = min(1.0, t / 0.008)
        decay = math.exp(-t * 2.2)
        envelope = attack * decay * velocity
        
        val = 0.0
        for mult, amp in harmonics:
            val += math.sin(2.0 * math.pi * freq * mult * t) * amp
            
        buffer[i] = val * envelope
    return buffer

def generate_track():
    left_channel = [0.0] * NUM_SAMPLES
    right_channel = [0.0] * NUM_SAMPLES
    
    print("[+] Synthesizing Studio Ghibli Acoustic Piano Song...")
    
    for start_time, note_str, dur, vel in melody_timeline:
        freq = note_to_freq(note_str)
        start_sample = int(start_time * SAMPLE_RATE)
        note_buf = synthesize_piano_note(freq, dur, vel)
        
        # Panning: lower notes center-left, higher notes right
        pan_right = min(0.8, max(0.2, (freq - 150) / 700))
        pan_left = 1.0 - pan_right
        
        for i, sample_val in enumerate(note_buf):
            target_idx = start_sample + i
            if target_idx < NUM_SAMPLES:
                left_channel[target_idx] += sample_val * pan_left
                right_channel[target_idx] += sample_val * pan_right

    # Add soft ambient string pad warmth in background
    print("[+] Adding Soft Ambient String Pad Layer...")
    for i in range(NUM_SAMPLES):
        t = i / SAMPLE_RATE
        pad_val = math.sin(2.0 * math.pi * 174.61 * t) * 0.03 + math.sin(2.0 * math.pi * 261.63 * t) * 0.02
        # Smooth loop fade at edges
        loop_fade = math.sin(math.pi * t / DURATION)
        left_channel[i] = (left_channel[i] + pad_val * loop_fade) * 0.85
        right_channel[i] = (right_channel[i] + pad_val * loop_fade) * 0.85

    # Normalize audio
    max_amp = max(max(abs(x) for x in left_channel), max(abs(x) for x in right_channel), 0.001)
    scale = 0.85 / max_amp
    
    output_path = os.path.join("audio", "ghibli_bg_music.wav")
    os.makedirs("audio", exist_ok=True)
    
    with wave.open(output_path, 'wb') as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2) # 16-bit PCM
        wav_file.setframerate(SAMPLE_RATE)
        
        interleaved = bytearray()
        for i in range(NUM_SAMPLES):
            l_sample = int(max(-32767, min(32767, left_channel[i] * scale * 32767)))
            r_sample = int(max(-32767, min(32767, right_channel[i] * scale * 32767)))
            interleaved.extend(struct.pack('<hh', l_sample, r_sample))
            
        wav_file.writeframes(interleaved)
        
    print(f"[+] Studio Ghibli Background Song generated: {output_path}")

if __name__ == "__main__":
    generate_track()
