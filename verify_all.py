import sys
from services.api_client import GoAcousticApiClient
from services.mock_data import generate_synthetic_audio, audio_to_wav_bytes
from components.audio_plots import plot_waveform, plot_stft_spectrogram, plot_mel_spectrogram, render_db_gauge_html
import matplotlib.pyplot as plt

def run_tests():
    print("Testing GoAcousticApiClient...")
    client = GoAcousticApiClient()
    health = client.check_health()
    print("[OK] Health check:", health)

    print("Testing synthetic audio generation...")
    y, sr, pred, peak = generate_synthetic_audio('Siren', 1.5)
    wav_bytes = audio_to_wav_bytes(y, sr)
    print(f"[OK] Synthetic Siren: {len(y)} samples, {sr} Hz, peak {peak} dB")

    upload_res = client.upload_audio(wav_bytes, 'test_siren.wav')
    print("[OK] Mock upload response:", upload_res['class'], upload_res['confidence'], upload_res['dB'])

    print("Testing Matplotlib & Librosa audio plotters...")
    fig1 = plot_waveform(y, sr)
    fig2 = plot_stft_spectrogram(y, sr)
    fig3 = plot_mel_spectrogram(y, sr)
    print("[OK] All 3 figures generated successfully!")
    plt.close('all')

    print("Testing History endpoint...")
    hist = client.get_history(limit=5)
    print(f"[OK] History returned {len(hist)} records")

    print("Testing Stream simulation packet...")
    pkt = client.simulate_stream_packet('Jackhammer')
    print("[OK] Stream packet:", pkt)

    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
