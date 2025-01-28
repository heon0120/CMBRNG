% LiveATC 오디오 스트림 URL
stream_url = 'https://s1-fmt2.liveatc.net/hf_nh_11396?nocache=2025012807413820484';

% 다운로드할 오디오 길이 (초)
duration = 10;

% FFmpeg 명령어
ffmpeg_cmd = sprintf('ffmpeg -i "%s" -t %d -f wav -ar 3000 -ac 1 pipe:1 > temp.wav', stream_url, duration);
system(ffmpeg_cmd);

% 오디오 데이터를 읽기
[audio_data, sample_rate] = audioread('temp.wav');

% 주파수 도메인으로 변환 (스펙트로그램 생성)
window_length = 256; % 윈도우 길이
overlap = 128;       % 오버랩 비율
[s, f, t] = spectrogram(audio_data, window_length, overlap, [], sample_rate);

% 로그 스케일로 변환
log_s = log(abs(s) + 1e-9); % 0으로 나누는 것을 방지하기 위해 작은 값을 더함

% 스펙트로그램을 0-255 범위로 정규화
normalized_spectrogram = uint8(255 * (log_s - min(log_s(:))) / (max(log_s(:)) - min(log_s(:))));

% 이미지를 출력하는 함수
figure;
imagesc(t, f, normalized_spectrogram);
axis xy; % Y축 방향을 올바르게 표시
colormap gray; % 흑백 색상 맵
axis off; % 축 제거
saveas(gcf, sprintf('%s.png', datestr(now, 'yyyymmddSS')), 'png'); % 현재 시간으로 파일 이름 저장
