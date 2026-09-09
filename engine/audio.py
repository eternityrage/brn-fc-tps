import numpy as np
import wave

def create_synchronized_audio(duration, win_moments, output_wav):
    sample_rate = 44100
    total_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, total_samples, endpoint=False)
    
    # 1. Subtle low suspense drone
    drone = 0.10 * np.sin(2 * np.pi * 60 * t)
    
    # 2. Metronome Clock Tick every 0.5s
    tick_sound = np.zeros(total_samples, dtype=np.float32)
    tick_len = int(0.04 * sample_rate)
    t_tick = np.linspace(0, 0.04, tick_len, endpoint=False)
    click = (np.sin(2 * np.pi * 1800 * t_tick) * np.exp(-t_tick * 120) * 0.4 +
             np.sin(2 * np.pi * 900 * t_tick) * np.exp(-t_tick * 80) * 0.25)
    
    for tick_time in np.arange(0.0, duration, 0.5):
        idx = int(tick_time * sample_rate)
        end_idx = min(idx + tick_len, total_samples)
        tick_sound[idx:end_idx] += click[:end_idx - idx]
        
    # 3. Alignment Chime on winning moments
    chime_sound = np.zeros(total_samples, dtype=np.float32)
    chime_len = int(0.35 * sample_rate)
    t_chime = np.linspace(0, 0.35, chime_len, endpoint=False)
    bell = (np.sin(2 * np.pi * 1046.5 * t_chime) + 0.5 * np.sin(2 * np.pi * 2093 * t_chime)) * np.exp(-t_chime * 10) * 0.4
    
    for w_time in win_moments:
        if w_time < duration:
            idx = int(w_time * sample_rate)
            end_idx = min(idx + chime_len, total_samples)
            chime_sound[idx:end_idx] += bell[:end_idx - idx]
            
    mix = drone + tick_sound + chime_sound
    mix = mix / (np.max(np.abs(mix)) + 1e-5) * 0.85
    audio_int16 = (mix * 32767).astype(np.int16)
    stereo = np.column_stack((audio_int16, audio_int16))
    
    # Write using standard library wave
    try:
        with wave.open(output_wav, 'wb') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(stereo.tobytes())
    except Exception:
        import scipy.io.wavfile as wavfile
        wavfile.write(output_wav, sample_rate, stereo)
