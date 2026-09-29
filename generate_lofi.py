import numpy as np
import scipy.io.wavfile as wavfile

# Parameters
sample_rate = 44100
duration = 38.0  # seconds (video is ~36.6s)
total_samples = int(sample_rate * duration)
t = np.linspace(0, duration, total_samples, endpoint=False)

# BPM and Timing
bpm = 88.0
beat_duration = 60.0 / bpm
bar_duration = beat_duration * 4

# Lo-Fi Rhodes / Electric Piano Chords (Upbeat, Warm, Hopeful progression)
# Progression in F major / D minor: Fmaj7 -> Am7 -> Bbmaj7 -> C7
# Fmaj7: F3 (174.61), A3 (220.0), C4 (261.63), E4 (329.63)
# Am7:   A3 (220.0), C4 (261.63), E4 (329.63), G4 (392.0)
# Bbmaj7: Bb3 (233.08), D4 (293.66), F4 (349.23), A4 (440.0)
# C7:    C3 (130.81), G3 (196.0), Bb3 (233.08), E4 (329.63)

chords = [
    [174.61, 220.0, 261.63, 329.63],   # Fmaj7
    [220.0, 261.63, 329.63, 392.0],     # Am7
    [233.08, 293.66, 349.23, 440.0],   # Bbmaj7
    [130.81, 196.0, 233.08, 329.63],   # C7
]

synth_audio = np.zeros(total_samples)

# Generate chords with gentle tremolo & envelope
num_bars = int(np.ceil(duration / bar_duration))
for bar_idx in range(num_bars):
    chord = chords[bar_idx % len(chords)]
    bar_start_sample = int(bar_idx * bar_duration * sample_rate)
    bar_samples = int(bar_duration * sample_rate)
    if bar_start_sample >= total_samples:
        break
    actual_samples = min(bar_samples, total_samples - bar_start_sample)
    local_t = np.linspace(0, actual_samples / sample_rate, actual_samples, endpoint=False)

    # Chord audio
    chord_sig = np.zeros(actual_samples)
    for freq in chord:
        # fundamental + warm 2nd harmonic
        note = np.sin(2 * np.pi * freq * local_t) + 0.35 * np.sin(4 * np.pi * freq * local_t) + 0.15 * np.sin(6 * np.pi * freq * local_t)
        chord_sig += note

    # ADSR Envelope (soft attack, sustained, subtle decay)
    env = np.ones(actual_samples)
    attack_samples = int(0.08 * sample_rate)
    decay_samples = int(0.4 * sample_rate)
    release_samples = int(0.3 * sample_rate)

    if actual_samples > attack_samples:
        env[:attack_samples] = np.linspace(0, 1, attack_samples)
    if actual_samples > release_samples:
        env[-release_samples:] = np.linspace(1, 0, release_samples)

    # Subtle tremolo (5 Hz)
    tremolo = 1.0 + 0.15 * np.sin(2 * np.pi * 4.8 * local_t)
    synth_audio[bar_start_sample:bar_start_sample + actual_samples] += chord_sig * env * tremolo * 0.18

# Bassline (warm low sine wave following root notes)
bass_audio = np.zeros(total_samples)
roots = [87.31, 110.0, 116.54, 130.81] # F2, A2, Bb2, C3
for bar_idx in range(num_bars):
    root_freq = roots[bar_idx % len(roots)]
    bar_start_sample = int(bar_idx * bar_duration * sample_rate)
    bar_samples = int(bar_duration * sample_rate)
    if bar_start_sample >= total_samples:
        break
    actual_samples = min(bar_samples, total_samples - bar_start_sample)
    local_t = np.linspace(0, actual_samples / sample_rate, actual_samples, endpoint=False)
    bass_sig = np.sin(2 * np.pi * root_freq * local_t) + 0.25 * np.sin(4 * np.pi * root_freq * local_t)
    bass_audio[bar_start_sample:bar_start_sample + actual_samples] += bass_sig * 0.25

# Upbeat Lo-Fi Drum Beat (Kick on 1 & 3, Snare/Clap on 2 & 4, swung Hi-hats)
drums = np.zeros(total_samples)
num_beats = int(np.ceil(duration / beat_duration))

for b in range(num_beats):
    beat_start = int(b * beat_duration * sample_rate)
    beat_sub = b % 4

    # Kick on beat 0 and syncopated beat 2.5
    if beat_sub == 0 or beat_sub == 2:
        kick_len = int(0.22 * sample_rate)
        if beat_start + kick_len <= total_samples:
            kt = np.linspace(0, 0.22, kick_len, endpoint=False)
            freq_drop = 140 * np.exp(-kt * 28) + 45
            phase = np.cumsum(freq_drop) / sample_rate
            kick = np.sin(2 * np.pi * phase) * np.exp(-kt * 18)
            drums[beat_start:beat_start + kick_len] += kick * 0.45

    # Snare on beat 1 and 3
    if beat_sub == 1 or beat_sub == 3:
        snare_len = int(0.18 * sample_rate)
        if beat_start + snare_len <= total_samples:
            st = np.linspace(0, 0.18, snare_len, endpoint=False)
            noise = np.random.normal(0, 1, snare_len) * np.exp(-st * 24)
            tonal = np.sin(2 * np.pi * 180 * st) * np.exp(-st * 30)
            drums[beat_start:beat_start + snare_len] += (noise * 0.35 + tonal * 0.25) * 0.5

    # Hi-Hats (8th notes with lo-fi swing)
    for sub in [0, 0.55]: # swung 8th
        hat_start = beat_start + int(sub * beat_duration * sample_rate)
        hat_len = int(0.045 * sample_rate)
        if hat_start + hat_len <= total_samples:
            ht = np.linspace(0, 0.045, hat_len, endpoint=False)
            hat = np.random.normal(0, 1, hat_len) * np.exp(-ht * 80)
            drums[hat_start:hat_start + hat_len] += hat * 0.12

# Subtle Vinyl Crackle / Ambient Texture
crackle = np.random.normal(0, 1, total_samples) * 0.015
# Pop occasionally
pops = np.random.choice([0, 1], size=total_samples, p=[0.9995, 0.0005]) * np.random.uniform(-0.15, 0.15, total_samples)

# Mixdown
final_mix = synth_audio + bass_audio + drums + crackle + pops
# Normalize
final_mix = final_mix / (np.max(np.abs(final_mix)) + 1e-6) * 0.85

# Convert to 16-bit PCM
final_mix_int16 = (final_mix * 32767).astype(np.int16)

out_wav = "/config/.gemini/antigravity/brain/50c5d83b-303c-4721-883f-1f56e36fbeb7/safehaven_lofi_music.wav"
wavfile.write(out_wav, sample_rate, final_mix_int16)
print(f"Generated upbeat lo-fi track: {out_wav} (Duration: {duration}s)")
