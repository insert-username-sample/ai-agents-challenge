import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel
import os

model_dir = r"D:\HuggingFace\hub\models--Qwen--Qwen3-TTS-12Hz-1.7B-Base\snapshots\fd4b254389122332181a7c3db7f27e918eec64e3"
ref_audio = r"C:\Users\Admin\Downloads\voice-clone-manas.wav"
ref_text = (
    "Okay, so this is an example of my audio being recorded. This is for one shot voice cloning. "
    "Let's see how well it does. Let's see. I mean, I'm really expecting it to do really well though. "
    "I don't know how well it will be though. I mean, it might be not that bad, but let's see how it does."
)

full_script = (
    "Modern AI systems are becoming increasingly capable. But they still struggle with two fundamental problems: assumptions and hallucinations. "
    "A response can appear correct, even when critical facts were never verified. "
    "Clausely was built to challenge generated outputs before they become conclusions. "
    "Built on Google's Agent Development Kit, Clausely combines Gemini 3.5 Flash, Grounding with Google Search, and a coordinated swarm of specialized agents working together in real time. "
    "A user query enters the system. Instead of committing to a single answer, Clausely generates multiple possible reasoning paths. "
    "Every path is continuously evaluated against grounded evidence. Facts, entities, dates, timelines, relationships, and citations are verified throughout the reasoning process, not just at the end. "
    "As grounded information enters the system, a swarm of specialized agents begins evaluating the generated paths. Some propose possibilities. Others search for weaknesses. Others verify evidence, challenge assumptions, and evaluate outcomes. "
    "During development, I noticed that my multi-agent verification approach closely aligned with the recently introduced AlphaProof Nexus framework by DeepMind. I subsequently adapted and refined parts of the system around those verification-driven principles. "
    "Rather than trusting the first response, Clausely continuously compares competing possibilities and pressure-tests them against available evidence. "
    "As new evidence arrives, unsupported paths are eliminated. Assumptions are challenged. Hallucinations are removed. Grounded paths continue forward. "
    "When critical information is missing, Clausely does not guess. The system pauses, requests clarification, and resumes only when sufficient information is available. "
    "In one real-world case, a generic model identified a petitioner as a daughter. Grounded evidence showed the judgment referred to a son. The unsupported path was eliminated, and the verified path remained. "
    "The result is a system designed not only to generate answers, but to verify them. "
    "Clausely explores how coordinated AI agents can reduce hallucinations, challenge assumptions, and produce more reliable outcomes."
)

print("Loading Qwen3-TTS model...")
model = Qwen3TTSModel.from_pretrained(
    model_dir,
    device_map="cuda:0",
    dtype=torch.bfloat16
)
print("Model loaded successfully.")

print("Creating voice clone prompt...")
clone_prompt = model.create_voice_clone_prompt(
    ref_audio=ref_audio,
    ref_text=ref_text
)
print("Voice clone prompt created.")

output_dir = r"g:\ai agents challenge\demo_video\assets"
os.makedirs(output_dir, exist_ok=True)

print("Generating single-track voiceover...")
try:
    wavs, sr = model.generate_voice_clone(
        text=full_script,
        language="English",
        voice_clone_prompt=clone_prompt,
        non_streaming_mode=True
    )
    out_path = os.path.join(output_dir, "full_voiceover.wav")
    sf.write(out_path, wavs[0], sr)
    print(f"SUCCESS: Single-track continuous voiceover saved to: {out_path}")
    print(f"Audio duration: {len(wavs[0]) / sr:.2f} seconds")
except Exception as e:
    print(f"ERROR generating single-track voiceover: {e}")
