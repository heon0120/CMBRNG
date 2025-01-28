import subprocess
import numpy as np
import librosa
from io import BytesIO


# LiveATC 오디오 스트림 URL
stream_url = "https://s1-fmt2.liveatc.net/hf_nh_11396?nocache=2025012807413820484"


def download_and_convert_audio_ffmpeg(url, duration=1.0):
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
            return None, None

        # Librosa로 데이터 읽기
        y, sr = librosa.load(BytesIO(wav_data), sr=None)
        return y, sr

    except Exception:
        return None, None


def find_first_positive_value(audio_data):
    audio_data_int16 = np.int16(audio_data * 32767)
    positive_indices = np.where(audio_data_int16 > 0)[0]  # 양의 값의 인덱스 찾기
    if positive_indices.size > 0:
        return audio_data_int16[positive_indices[0]]  # 첫 번째 양의 값 반환
    return None


def shift_array_and_get_values(audio_data, shift_amount, num):
    audio_data_int16 = np.int16(audio_data * 32767)
    shifted_index = max(len(audio_data_int16) - shift_amount, 0)
    return audio_data_int16[shifted_index:shifted_index + num]


def extract_last_two_digits(values):
    return np.abs(values % 100)  # 음수를 처리하기 위해 절댓값 사용


def map_to_ascii(value):
    if 0 <= value <= 9:
        return str(value)
    elif 10 <= value <= 35:
        return chr(ord('A') + (value - 10))
    elif 36 <= value <= 61:
        return chr(ord('a') + (value - 36))
    else:
        return str(value)


def generator(num):
    while True:
        audio_data, sample_rate = download_and_convert_audio_ffmpeg(stream_url, duration=10)
        if audio_data is not None:
            first_positive = find_first_positive_value(audio_data)
            if first_positive is not None:
                shifted_values = shift_array_and_get_values(audio_data, first_positive, num)
                last_two_digits = extract_last_two_digits(shifted_values)
                ascii_values = [map_to_ascii(digit) for digit in last_two_digits]
                result_string = ''.join(ascii_values)[:num]
                result_string = result_string.replace(' ', '').replace('\n', '')

                if len(result_string) == num:
                    return result_string
        # 데이터가 None이거나 조건을 만족하지 않으면 다시 시도

