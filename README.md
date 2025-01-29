# CMBRNG
Generate random number using Cosmic Microwave Background Radiation

# What is it?
본 코드는 우주배경복사가 포함된 잡음 오디오 데이터를 수집해 배열로 만든후 난수를 추출하는 코드입니다.(LiveATC에서 한적한 공항의ATC신호를 받아옴) 신뢰할 수 있는 난수로 간주될 수는 없지만 일반적인 의사난수(Pseudo-random Number)보다 독특한 특성을 가질 수 있습니다.

## 코드 설명

### 1. `download_and_convert_audio_ffmpeg`

LiveATC 스트림에서 데이터를 다운로드하고 변환하는 함수입니다.  
`FFmpeg`를 사용하여 스트림 데이터를 WAV 형식으로 변환하며, `Librosa`를 통해 배열 형태로 로드합니다.

```python
def download_and_convert_audio_ffmpeg(url, duration=0.1):
    ffmpeg_cmd = [
        "ffmpeg", "-i", url, "-t", str(duration), 
        "-f", "wav", "-ar", "3000", "-ac", "1", "pipe:1"
    ]
    process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    wav_data, error = process.communicate()
    
    if process.returncode != 0:
        return None
    return librosa.load(BytesIO(wav_data), sr=None)[0]
```
### 2. `find_first_positive_value`


오디오 데이터에서 첫 번째 양의 값을 찾는 함수입니다.
이 값은 이후 데이터를 이동하는 기준이 됩니다.
```python
def find_first_positive_value(data):
    positive_values = data[data > 0]
    return positive_values[0] if len(positive_values) > 0 else None
```


### 3. `shift_array_and_get_values`
배열에서 양의 값을 기준으로 이동하여 난수 데이터로 사용할 값들을 추출합니다.
```python
def shift_array_and_get_values(data, shift, num):
    start_index = max(0, len(data) - shift)
    return data[start_index : start_index + num]

```


### 4. `map_to_ascii`
난수 데이터를 ASCII 문자로 변환합니다.
대문자(A-Z), 소문자(a-z), 숫자(0-9) 범위만 허용합니다.
```python
def map_to_ascii(values):
    result = []
    for value in values:
        if 48 <= value <= 57 or 65 <= value <= 90 or 97 <= value <= 122:
            result.append(chr(value))
        else:
            result.append(str(value))
    return ''.join(result)
```


### 5. `generator`
난수를 생성하는 핵심 함수입니다.
주어진 길이(num)의 난수를 생성하며, 유효한 결과가 나올 때까지 반복합니다.
```python
def generator(num):
    stream_url = "https://s1-fmt2.liveatc.net/hf_nh_11396"
    while True:
        audio_data = download_and_convert_audio_ffmpeg(stream_url, duration=0.1)
        if audio_data is None:
            continue

        first_positive = find_first_positive_value(audio_data)
        if first_positive is None:
            continue

        shifted_values = shift_array_and_get_values(audio_data, int(first_positive), num)
        extracted_digits = extract_last_two_digits(shifted_values)
        result = map_to_ascii(extracted_digits)

        if len(result) == num:
            return result
```

## 실행 방법

### 환경 설정

1. 필요 라이브러리 설치:
   ```bash
   pip install numpy librosa
   sudo apt-get install ffmpeg
   ```
2. 코드실행:
```python
from generator import generator
result = generator(100)
print(result)
```


## 다른 코드 설명

fastgenerator(test).py: 기존코드를 병렬처리를 통하여 빠르게 연산하도록 제작하였습니다. 기본적으로 4개의 워커가 있습니다. 4개 이상부터는 step_size가 작아져 None이 반환됩니다.

choice_include.py: random의 choice기능을 추가하였습니다.
```python
from choice_include import Generator
# Generator 클래스 사용 예시
gen = Generator(workers=4)
options = ["Alpha", "Bravo", "Charlie", "Delta"]
result = Generator(workers=4).choice(options)  # options 중에서 선택
print("Choice result:", result)

```
로 사용할수있습니다.


출력결과 :
```
Choice result: Charlie
```


