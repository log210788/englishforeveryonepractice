import subprocess
import os

ps_script = """
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SetOutputToWaveFile("e:/class aids/code/englishForEveryoneOne/audio/4/4_1_4.wav")
$synth.Speak("uncle")
$synth.Dispose()
"""

with open("scratch/gen_audio.ps1", "w", encoding="utf-8") as f:
    f.write(ps_script)

res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "scratch/gen_audio.ps1"], capture_output=True, text=True)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)

wav_path = "audio/4/4_1_4.wav"
mp3_path = "audio/4/4_1_4.mp3"

if os.path.exists(wav_path):
    print(f"Generated {wav_path}, size: {os.path.getsize(wav_path)} bytes")
    # Copy or rename to 4_1_4.mp3 so HTML audio elements load it seamlessly!
    with open(wav_path, "rb") as rf, open(mp3_path, "wb") as wf:
        wf.write(rf.read())
    print(f"Successfully updated {mp3_path}, size: {os.path.getsize(mp3_path)} bytes")
