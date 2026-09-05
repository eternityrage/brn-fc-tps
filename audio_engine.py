import numpy as np
import scipy.io.wavfile as wavfile
import os

def generate_challenge_audio(duration=8.0, sample_rate=44100, output_wav="C:/Users/kreg9/viral_puzzle_reels/audio_track.wav"):
    """
    Generates a rhythmic, suspenseful sound track:
    - Metronome / clock tick every 0.5s (120 BPM)
    - Low suspense heartbeat pulse
    - Rhythmic swoosh effects
    - Ding/bell on alignment moments
    """
    total_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, total_samples, endpoint=False)
    
    # 1. Subtle low suspense drone (55 Hz low rumble)
    drone = 0.12 * np.sin(2 * np.pi * 55 * t)
    
    # 2. Clock Tick / Metronome (every 0.5s)
    tick_sound = np.zeros(total_samples, dtype=np.float32)
    tick_interval = 0.5 # 120 BPM
    tick_len = int(0.04 * sample_rate) # 40ms click
    t_tick = np.linspace(0, 0.04, tick_len, endpoint=False)
    # Metronome click waveform: damped sine wave at 1800Hz and 900Hz
    click = np.sin(2 * np.pi * 1800 * t_tick) * np.exp(-t_tick * 120) * 0.4
    click += np.sin(2 * np.pi * 900 * t_tick) * np.exp(-t_tick * 80) * 0.25
    
    for tick_time in np.arange(0.0, duration, tick_interval):
        idx = int(tick_time * sample_rate)
        end_idx = min(idx + tick_len, total_samples)
        tick_sound[idx:end_idx] += click[:end_idx - idx]
        
    # 3. Soft oscillation swoosh (synced with movement frequency ~0.6 Hz)
    swoosh_env = 0.5 * (1.0 + np.sin(2 * np.pi * 1.2 * t - np.pi/2)) # peaks every ~0.8s
    # Filtered white noise for whoosh
    noise = np.random.uniform(-1, 1, total_samples)
    # Simple lowpass filter on noise
    kernel_size = 50
    noise_smooth = np.convolve(noise, np.ones(kernel_size)/kernel_size, mode='same')
    swoosh = noise_smooth * swoosh_env * 0.18
    
    # 4. Alignment Chime / Ding at winning moments (e.g. 2.35s, 4.35s, 6.35s)
    chime_sound = np.zeros(total_samples, dtype=np.float32)
    chime_len = int(0.3 * sample_rate)
    t_chime = np.linspace(0, 0.3, chime_len, endpoint=False)
    # Beautiful bell/chime harmonics: 1046 Hz (C6) + 2093 Hz (C7)
    bell = (np.sin(2 * np.pi * 1046.5 * t_chime) + 0.5 * np.sin(2 * np.pi * 2093 * t_chime)) * np.exp(-t_chime * 12) * 0.35
    
    for win_time in [2.35, 4.35, 6.35]:
        if win_time < duration:
            idx = int(win_time * sample_rate)
            end_idx = min(idx + chime_len, total_samples)
            chime_sound[idx:end_idx] += bell[:end_idx - idx]

    # Mix together
    mix = drone + tick_sound + swoosh + chime_sound
    
    # Normalize to prevent clipping
    mix = mix / (np.max(np.abs(mix)) + 1e-5) * 0.9
    
    # Convert to 16-bit PCM
    audio_int16 = (mix * 32767).astype(np.int16)
    
    # Save stereo (duplicate to 2 channels)
    stereo = np.column_stack((audio_int16, audio_int16))
    wavfile.write(output_wav, sample_rate, stereo)
    print(f"Generated high quality audio: {output_wav} ({os.path.getsize(output_wav)} bytes)")
    return output_wav

if __name__ == "__main__":
    generate_challenge_audio(8.0)
