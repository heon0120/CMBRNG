import subprocess
import numpy as np
import librosa
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed

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
    positive_indices = np.where(audio_data_int16 > 0)[0]
    if positive_indices.size > 0:
        return audio_data_int16[positive_indices[0]]
    return None


def shift_array_and_get_values(audio_data, shift_amount, num):
    audio_data_int16 = np.int16(audio_data * 32767)
    shifted_index = max(len(audio_data_int16) - shift_amount, 0)
    return audio_data_int16[shifted_index:shifted_index + num]


def extract_last_two_digits(values):
    return np.abs(values % 100)


def map_to_ascii(value):
    if 0 <= value <= 9:
        return str(value)
    elif 10 <= value <= 35:
        return chr(ord('A') + (value - 10))
    elif 36 <= value <= 61:
        return chr(ord('a') + (value - 36))
    else:
        return str(value)


def process_audio(num, start_index, step_size):
    audio_data, sample_rate = download_and_convert_audio_ffmpeg(stream_url, duration=10)
    if audio_data is not None:
        first_positive = find_first_positive_value(audio_data)
        if first_positive is not None:
            shifted_values = shift_array_and_get_values(audio_data, first_positive + start_index, num)
            last_two_digits = extract_last_two_digits(shifted_values)
            ascii_values = [map_to_ascii(digit) for digit in last_two_digits]
            result_string = ''.join(ascii_values)[:num]
            result_string = result_string.replace(' ', '').replace('\n', '')

            if len(result_string) == num:
                return result_string
    return None


def generator_function(num, workers=4):
    step_size = num // workers  # 각 워커가 처리할 값의 크기
    futures = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        # 각 워커가 일정 구간을 처리하도록 작업 분할
        for i in range(workers):
            start_index = i * step_size
            futures.append(executor.submit(process_audio, step_size, start_index, step_size))

        # 각 워커의 결과를 결합
        result_list = []
        for future in as_completed(futures):
            res = future.result()
            if res is not None:
                result_list.append(res)

    # 결과 문자열 결합 및 길이 조정
    final_result = ''.join(result_list)
    return final_result[:num] if len(final_result) >= num else None


class Generator:
    def __init__(self, workers=4):
        self.workers = workers

    def choice(self, sequences):
        """sequences 리스트에서 가장 큰 값을 가진 문자열을 선택"""
        generated_values = generator_function(len(sequences), workers=self.workers)
        if generated_values:
            max_index = np.argmax([sum(map(ord, val)) for val in generated_values])
            return sequences[max_index]
        return None

    def __call__(self, num, workers=None):
        """기존 generator_function을 사용할 수 있도록 호출 가능하게 만듦"""
        if workers is None:
            workers = self.workers
        return generator_function(num, workers=workers)
