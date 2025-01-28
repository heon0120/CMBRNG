import subprocess
import numpy as np
import librosa
from io import BytesIO
from datetime import datetime

# LiveATC 오디오 스트림 URL
stream_url = "https://s1-fmt2.liveatc.net/hf_nh_11396?nocache=2025012807413820484"
now = datetime.now()

# yyyymmddss 형식으로 출력
formatted_date = now.strftime("%Y%m%d%S")


def download_and_convert_audio_ffmpeg(url, duration=0.005):
    try:
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", url,
            "-t", str(duration),
            "-f", "wav",
            "-ar", "3000",
            "-ac", "1",
            "pipe:1"
        ]
        process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        wav_data, error = process.communicate()

        if process.returncode != 0:
            print(f"FFmpeg error: {error.decode()}")
            return None, None

        y, sr = librosa.load(BytesIO(wav_data), sr=None)
        return y, sr

    except Exception as e:
        print(f"Error: {e}")
        return None, None


def audio_to_ascii_or_number(audio_data):
    audio_data_int16 = np.int16(audio_data * 32767)
    ascii_result = []

    for value in audio_data_int16:
        # 2자리 숫자로 나누기
        two_digit_number = abs(value) % 100
        # ASCII로 변환 가능한 경우
        if 0 <= two_digit_number < 128:
            ascii_result.append(chr(two_digit_number))
        else:
            ascii_result.append(str(two_digit_number))  # 숫자로 저장

    return ''.join(ascii_result)


def save_to_binary(data, filename):
    with open(filename, 'wb') as f:
        f.write(data.encode('ascii', 'ignore'))


# 실제 코드 실행
url = stream_url
audio_data, sample_rate = download_and_convert_audio_ffmpeg(url, duration=10)
if audio_data is not None:
    ascii_representation = audio_to_ascii_or_number(audio_data)

    # ASCII 데이터를 바이너리 파일로 저장
    binary_filename = formatted_date + '.bin'
    save_to_binary(ascii_representation, binary_filename)
    print(f"ASCII 또는 숫자로 변환된 데이터를 바이너리 파일로 저장했습니다: {binary_filename}")
else:
    print("오디오 데이터를 처리할 수 없습니다.")
