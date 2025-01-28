import subprocess
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime
# LiveATC 오디오 스트림 URL
stream_url = "https://s1-fmt2.liveatc.net/hf_nh_11396?nocache=2025012807413820484"
now = datetime.now()

# yyyymmddss 형식으로 출력
formatted_date = now.strftime("%Y%m%d%S")
def download_and_convert_audio_ffmpeg(url, duration=0.005):
    """
    FFmpeg를 사용해 스트림 데이터를 WAV로 변환
    :param url: 스트리밍 URL
    :param duration: 다운로드할 오디오 길이 (초)
    :return: 오디오 데이터 (numpy 배열)와 샘플링 속도
    """
    try:
        # FFmpeg 명령어
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", url,          # 입력 스트림 URL
            "-t", str(duration), # 다운로드할 길이
            "-f", "wav",        # 출력 형식 (WAV)
            "-ar", "16000",     # 샘플링 속도 (16kHz)
            "-ac", "1",         # 채널 수 (모노)
            "pipe:1"            # 표준 출력으로 내보내기
        ]
        # FFmpeg 실행
        process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        wav_data, error = process.communicate()

        if process.returncode != 0:
            print(f"FFmpeg error: {error.decode()}")
            return None, None

        # librosa로 WAV 데이터 로드
        y, sr = librosa.load(BytesIO(wav_data), sr=None)
        return y, sr

    except Exception as e:
        print(f"Error: {e}")
        return None, None


# 오디오 데이터를 주파수 도메인으로 변환 (FFT 사용)
def audio_to_spectrogram(audio_data, rate):
    # STFT를 통해 오디오 데이터를 주파수 도메인으로 변환
    stft_data = np.abs(librosa.stft(audio_data))

    # 로그 스케일로 변환
    log_stft = np.log(stft_data + 1e-9)  # 0으로 나누는 것을 방지하기 위해 작은 값을 더함

    # 스펙트로그램을 0-255 범위로 정규화
    spectrogram = np.interp(log_stft, (log_stft.min(), log_stft.max()), (0, 255))

    return spectrogram.astype(np.uint8)


# 이미지를 출력하는 함수
def plot_spectrogram(spectrogram_data):
    plt.imshow(spectrogram_data, cmap='gray', aspect='auto')
    plt.axis('off')  # 축 제거
    plt.savefig(formatted_date + '.png', dpi=300)
    plt.show()


# 실제 코드 실행
url = 'https://s1-fmt2.liveatc.net/hf_nh_11396?nocache=2025012807413820484'  # 스트리밍 URL
audio_data, sample_rate = download_and_convert_audio_ffmpeg(url, duration=10)
if audio_data is not None:
    spectrogram_data = audio_to_spectrogram(audio_data, sample_rate)
    plot_spectrogram(spectrogram_data)
else:
    print("오디오 데이터를 처리할 수 없습니다.")
