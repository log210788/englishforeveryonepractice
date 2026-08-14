import subprocess
import os

ps_content = """Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Rate = 0
$synth.Volume = 100
$synth.SetOutputToWaveFile("e:/class aids/code/englishForEveryoneOne/audio/4/4_1_3.wav")
$synth.Speak("sister")
$synth.Dispose()
"""

with open("scratch/make_sister.ps1", "w", encoding="utf-8") as f:
    f.write(ps_content)

res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "scratch/make_sister.ps1"], capture_output=True, text=True)
print("PowerShell STDOUT:", res.stdout)
print("PowerShell STDERR:", res.stderr)

wav_file = "audio/4/4_1_3.wav"
mp3_file = "audio/4/4_1_3.mp3"

if os.path.exists(wav_file):
    with open(wav_file, "rb") as rf, open(mp3_file, "wb") as wf:
        wf.write(rf.read())
    print(f"Updated {mp3_file} with 'sister' audio, size: {os.path.getsize(mp3_file)} bytes")
