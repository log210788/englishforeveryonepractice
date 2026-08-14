#!/usr/bin/env python3
"""
Generates organic Studio Ghibli sound effects:
1. audio/ghibli_click.wav - Soft wooden kalimba / marimba click
2. audio/ghibli_waterdrop.wav - Forest dewdrop / water plop click
3. audio/ghibli_chime.wav - Soft acoustic bell chime
"""

import math
import struct
import wave
import os

SAMPLE_RATE = 44100

def write_wav(filename, samples):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'wb') as f:
        f.setnchannels(1) # Mono
        f.setsampwidth(2) # 16-bit PCM
        f.setframerate(SAMPLE_RATE)
        
        # Normalize
        max_amp = max(abs(s) for s in samples) or 1.0
        scale = 0.85 / max_amp
        
        interleaved = bytearray()
        for s in samples:
            val = int(max(-32767, min(32767, s * scale * 32767)))
            interleaved.extend(struct.pack('<h', val))
        f.writeframes(interleaved)
    print(f"[+] Generated {filename}")

def gen_kalimba_click():
    # Soft wooden kalimba note (C5 523.25Hz with 2nd and 3rd harmonics + lowpass decay)
    duration = 0.18
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    freq = 523.25 # C5
    
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Envelope: 3ms attack, exponential decay
        attack = min(1.0, t / 0.003)
        decay = math.exp(-t * 22.0)
        env = attack * decay
        
        # Harmonics
        val = (math.sin(2 * math.pi * freq * t) * 1.0 +
               math.sin(2 * math.pi * freq * 2 * t) * 0.35 +
               math.sin(2 * math.pi * freq * 3 * t) * 0.12)
        samples.append(val * env)
    return samples

def gen_waterdrop_click():
    # Dewdrop pitch glide from 360Hz to 560Hz with soft resonance
    duration = 0.08
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Exponential frequency glide
        freq = 360.0 * math.pow(560.0 / 360.0, t / duration)
        attack = min(1.0, t / 0.002)
        decay = math.exp(-t * 35.0)
        env = attack * decay
        
        val = math.sin(2 * math.pi * freq * t) + math.sin(2 * math.pi * freq * 0.5 * t) * 0.2
        samples.append(val * env)
    return samples

def gen_chime():
    # Gentle Ghibli triad chime (C5, E5, G5)
    duration = 0.6
    num_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * num_samples
    notes = [523.25, 659.25, 783.99]
    
    for idx, freq in enumerate(notes):
        delay_t = idx * 0.08
        delay_samples = int(delay_t * SAMPLE_RATE)
        for i in range(num_samples - delay_samples):
            t = i / SAMPLE_RATE
            attack = min(1.0, t / 0.005)
            decay = math.exp(-t * 6.0)
            env = attack * decay * 0.4
            val = math.sin(2 * math.pi * freq * t) + math.sin(2 * math.pi * freq * 2 * t) * 0.2
            samples[delay_samples + i] += val * env
            
    return samples

if __name__ == '__main__':
    write_wav(os.path.join('audio', 'ghibli_click.wav'), gen_kalimba_click())
    write_wav(os.path.join('audio', 'ghibli_waterdrop.wav'), gen_waterdrop_click())
    write_wav(os.path.join('audio', 'ghibli_chime.wav'), gen_chime())
