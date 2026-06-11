import os
import numpy as np
import soundfile as sf

assets_dir = r"g:\ai agents challenge\demo_video\assets"
beat_names = [f"beat{i}" for i in range(1, 15)]

combined_audio = []
current_time = 0.0
sample_rate = None

beat_timings = {}
silence_sec = 0.65  # Silent pause between beats for natural pacing

for name in beat_names:
    path = os.path.join(assets_dir, f"{name}.wav")
    if not os.path.exists(path):
        print(f"Error: {path} not found.")
        continue
    data, sr = sf.read(path)
    if sample_rate is None:
        sample_rate = sr
    
    duration = len(data) / sr
    beat_timings[name] = {
        "start": current_time,
        "end": current_time + duration,
        "duration": duration
    }
    
    combined_audio.append(data)
    
    if name != "beat14":
        silence_samples = int(silence_sec * sr)
        if len(data.shape) > 1:
            silence = np.zeros((silence_samples, data.shape[1]))
        else:
            silence = np.zeros(silence_samples)
        combined_audio.append(silence)
        current_time += duration + silence_sec
    else:
        current_time += duration

final_audio = np.concatenate(combined_audio, axis=0)
out_path = os.path.join(assets_dir, "full_voiceover.wav")
sf.write(out_path, final_audio, sample_rate)

print(f"SUCCESS: Stitched file saved to {out_path}")
print(f"TOTAL_DURATION: {current_time:.2f}")
print("TIMINGS:")
for name, times in beat_timings.items():
    print(f"{name}: start={times['start']:.2f}, end={times['end']:.2f}, duration={times['duration']:.2f}")
