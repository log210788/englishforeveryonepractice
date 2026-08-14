import subprocess
import os

def generate_tts_wav_mp3(word, base_name):
    wav_path = f"audio/4/{base_name}.wav"
    mp3_path = f"audio/4/{base_name}.mp3"
    
    ps_script = f"""
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SetOutputToWaveFile("e:/class aids/code/englishForEveryoneOne/{wav_path}")
$synth.Speak("{word}")
$synth.Dispose()
"""
    ps_file = f"scratch/gen_{base_name}.ps1"
    with open(ps_file, "w", encoding="utf-8") as f:
        f.write(ps_script)

    res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_file], capture_output=True, text=True)
    if os.path.exists(wav_path):
        with open(wav_path, "rb") as rf, open(mp3_path, "wb") as wf:
            wf.write(rf.read())
        print(f"Successfully generated {mp3_path} ({word}), size: {os.path.getsize(mp3_path)} bytes")
    else:
        print(f"Error generating {wav_path}: {res.stderr}")

# 1. Generate audio for "sister" -> 4_1_3.mp3
generate_tts_wav_mp3("sister", "4_1_3")

# 2. Generate audio for "uncle" -> 4_1_4.mp3
generate_tts_wav_mp3("uncle", "4_1_4")
