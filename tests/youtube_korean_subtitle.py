"""
YouTube 동영상 → 한글 자막 변환기 (MAI-Transcribe-1)

유튜브 동영상의 음성을 추출한 뒤 MAI-Transcribe-1 LLM Speech API로
한국어 자막(SRT)을 생성합니다.

사전 준비:
  pip install yt-dlp azure-ai-transcription azure-identity python-dotenv

.env 파일:
  AZURE_MAI_SPEECH_RESOURCE_ID - Azure Cognitive Services 리소스 ID
    (예: /subscriptions/.../providers/Microsoft.CognitiveServices/accounts/<name>)

인증:
  az login 으로 Azure CLI 로그인 후 DefaultAzureCredential 사용 (keyless)

사용법:
  python youtube_korean_subtitle.py "https://www.youtube.com/watch?v=VIDEO_ID"
  python youtube_korean_subtitle.py "https://www.youtube.com/watch?v=VIDEO_ID" --output subtitles.srt
  python youtube_korean_subtitle.py "https://www.youtube.com/watch?v=VIDEO_ID" --source-locale ja-JP
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv

# .env 파일 로드 (스크립트와 같은 디렉토리)
load_dotenv(Path(__file__).parent / ".env")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

RESOURCE_ID = os.environ.get("AZURE_MAI_SPEECH_RESOURCE_ID", "")


def _resource_name_from_id(resource_id: str) -> str:
    """Azure 리소스 ID에서 리소스 이름을 추출합니다."""
    # /subscriptions/.../providers/Microsoft.CognitiveServices/accounts/<name>
    parts = resource_id.rstrip("/").split("/")
    if len(parts) >= 2 and parts[-2].lower() == "accounts":
        return parts[-1]
    raise ValueError(f"리소스 ID에서 이름을 추출할 수 없습니다: {resource_id}")


def _get_endpoint() -> str:
    """리소스 ID에서 엔드포인트 URL을 생성합니다."""
    if not RESOURCE_ID:
        raise ValueError(
            "AZURE_MAI_SPEECH_RESOURCE_ID 환경 변수를 .env 파일에 설정하세요."
        )
    name = _resource_name_from_id(RESOURCE_ID)
    return f"https://{name}.cognitiveservices.azure.com"


# Fast Transcription API 오디오 파일 크기 제한: 300 MB
MAX_AUDIO_SIZE_BYTES = 300 * 1024 * 1024

# 청크 분할 기준 (10분 단위)
CHUNK_DURATION_SEC = 600


# ---------------------------------------------------------------------------
# 1. YouTube 오디오 추출
# ---------------------------------------------------------------------------


def extract_audio_from_youtube(url: str, output_dir: str | None = None) -> str:
    """yt-dlp를 사용하여 YouTube 동영상에서 오디오를 WAV로 추출합니다.

    Args:
        url: YouTube 동영상 URL
        output_dir: 출력 디렉토리 (None이면 임시 디렉토리 사용)

    Returns:
        추출된 WAV 파일 경로
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="yt_audio_")

    output_path = os.path.join(output_dir, "audio.wav")

    cmd = [
        "yt-dlp",
        "--no-playlist",
        "--extract-audio",
        "--audio-format", "wav",
        "--audio-quality", "0",
        "--postprocessor-args", "ffmpeg:-ac 1 -ar 16000",
        "--output", output_path,
        url,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(
            f"yt-dlp 오디오 추출 실패 (exit code {result.returncode}):\n"
            f"stderr: {result.stderr}"
        )

    # yt-dlp가 확장자를 변경할 수 있으므로 실제 파일 확인
    if not os.path.exists(output_path):
        # .wav 대신 다른 확장자로 저장됐을 수 있음
        candidates = list(Path(output_dir).glob("audio.*"))
        if candidates:
            output_path = str(candidates[0])
        else:
            raise FileNotFoundError(
                f"추출된 오디오 파일을 찾을 수 없습니다: {output_dir}"
            )

    return output_path


# ---------------------------------------------------------------------------
# 2. 오디오 청크 분할 (대용량 파일 처리)
# ---------------------------------------------------------------------------


def split_audio_into_chunks(
    audio_path: str, chunk_duration_sec: int = CHUNK_DURATION_SEC
) -> list[str]:
    """긴 오디오 파일을 청크로 분할합니다.

    Args:
        audio_path: 원본 오디오 파일 경로
        chunk_duration_sec: 청크 길이(초)

    Returns:
        분할된 청크 파일 경로 리스트
    """
    file_size = os.path.getsize(audio_path)
    if file_size <= MAX_AUDIO_SIZE_BYTES:
        return [audio_path]

    output_dir = os.path.dirname(audio_path)
    chunk_pattern = os.path.join(output_dir, "chunk_%03d.wav")

    cmd = [
        "ffmpeg", "-i", audio_path,
        "-f", "segment",
        "-segment_time", str(chunk_duration_sec),
        "-ac", "1", "-ar", "16000",
        "-c:a", "pcm_s16le",
        chunk_pattern,
        "-y",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg 청크 분할 실패:\n{result.stderr}")

    chunks = sorted(Path(output_dir).glob("chunk_*.wav"))
    return [str(c) for c in chunks]


# ---------------------------------------------------------------------------
# 3. MAI-Transcribe-1 한국어 번역 요청
# ---------------------------------------------------------------------------


def translate_audio_to_korean(
    audio_path: str,
    *,
    source_locale: str = "en-US",
    prompt: list[str] | None = None,
) -> dict:
    """MAI-Transcribe-1 LLM Speech API로 오디오를 한국어로 번역합니다.

    azure-ai-transcription SDK + DefaultAzureCredential (keyless) 사용.

    Args:
        audio_path: 오디오 파일 경로
        source_locale: 소스 오디오 언어 로케일
        prompt: 번역 지시 프롬프트 (선택)

    Returns:
        API 응답을 dict로 변환한 결과
    """
    from azure.identity import DefaultAzureCredential
    from azure.ai.transcription import TranscriptionClient
    from azure.ai.transcription.models import (
        TranscriptionContent,
        TranscriptionOptions,
        EnhancedModeProperties,
    )

    endpoint = _get_endpoint()
    credential = DefaultAzureCredential()

    client = TranscriptionClient(endpoint=endpoint, credential=credential)

    if prompt is None:
        prompt = [
            "Translate the audio to Korean.",
            "Format as natural Korean subtitle text.",
            "Keep sentences short and concise.",
        ]

    enhanced_mode = EnhancedModeProperties(
        task="translate",
        target_language="ko",
        prompt=prompt,
    )

    options = TranscriptionOptions(
        locales=[source_locale],
        enhanced_mode=enhanced_mode,
    )

    with open(audio_path, "rb") as audio_file:
        request_content = TranscriptionContent(definition=options, audio=audio_file)
        result = client.transcribe(request_content)

    # SDK 결과를 dict로 변환하여 하위 함수와 호환
    result_dict = {}
    if result.combined_phrases:
        result_dict["combinedPhrases"] = [
            {"text": p.text} for p in result.combined_phrases
        ]
    if result.phrases:
        result_dict["phrases"] = [
            {
                "text": p.text,
                "offsetMilliseconds": getattr(p, "offset_milliseconds", 0),
                "durationMilliseconds": getattr(p, "duration_milliseconds", 3000),
            }
            for p in result.phrases
        ]
    return result_dict


# ---------------------------------------------------------------------------
# 4. SRT 자막 생성
# ---------------------------------------------------------------------------


def _ms_to_srt_time(ms: int) -> str:
    """밀리초를 SRT 타임코드 형식으로 변환합니다 (HH:MM:SS,mmm)."""
    hours = ms // 3_600_000
    ms %= 3_600_000
    minutes = ms // 60_000
    ms %= 60_000
    seconds = ms // 1_000
    millis = ms % 1_000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def build_srt(
    phrases: list[dict], *, time_offset_ms: int = 0
) -> tuple[str, int]:
    """API 응답의 phrases 리스트를 SRT 형식 문자열로 변환합니다.

    Args:
        phrases: API 응답의 phrases 리스트
        time_offset_ms: 청크별 시간 오프셋(밀리초)

    Returns:
        (SRT 문자열, 마지막 자막 번호)
    """
    srt_lines = []
    idx = 1

    for i, phrase in enumerate(phrases):
        offset = phrase.get("offsetMilliseconds", phrase.get("offset", 0))
        duration = phrase.get("durationMilliseconds", phrase.get("duration", 3000))
        text = phrase.get("text", "")

        if not text.strip():
            continue

        start_ms = offset + time_offset_ms
        end_ms = start_ms + duration

        srt_lines.append(str(idx))
        srt_lines.append(f"{_ms_to_srt_time(start_ms)} --> {_ms_to_srt_time(end_ms)}")
        srt_lines.append(text.strip())
        srt_lines.append("")
        idx += 1

    return "\n".join(srt_lines), idx - 1


def build_srt_from_combined(combined_text: str, duration_ms: int = 5000) -> str:
    """combinedPhrases 텍스트를 간단한 SRT로 변환합니다 (phrases가 없을 때 폴백)."""
    sentences = [s.strip() for s in combined_text.replace(".", ".\n").split("\n") if s.strip()]
    srt_lines = []

    for i, sentence in enumerate(sentences):
        start_ms = i * duration_ms
        end_ms = start_ms + duration_ms

        srt_lines.append(str(i + 1))
        srt_lines.append(f"{_ms_to_srt_time(start_ms)} --> {_ms_to_srt_time(end_ms)}")
        srt_lines.append(sentence)
        srt_lines.append("")

    return "\n".join(srt_lines)


# ---------------------------------------------------------------------------
# 5. 전체 파이프라인
# ---------------------------------------------------------------------------


def youtube_to_korean_srt(
    youtube_url: str,
    *,
    output_path: str | None = None,
    source_locale: str = "en-US",
) -> str:
    """YouTube 동영상 → 한국어 SRT 자막 변환 파이프라인.

    Args:
        youtube_url: YouTube 동영상 URL
        output_path: 저장할 SRT 파일 경로 (None이면 자동 생성)
        source_locale: 소스 오디오 언어 (기본 en-US)

    Returns:
        생성된 SRT 파일 경로
    """
    print(f"[1/4] YouTube 오디오 추출 중: {youtube_url}")
    audio_path = extract_audio_from_youtube(youtube_url)

    print(f"[2/4] 오디오 청크 분할 확인 중...")
    chunks = split_audio_into_chunks(audio_path)
    print(f"       → {len(chunks)}개 청크")

    all_srt_parts = []
    time_offset_ms = 0
    subtitle_count = 0

    for i, chunk_path in enumerate(chunks):
        print(f"[3/4] 한국어 번역 중... ({i + 1}/{len(chunks)})")
        result = translate_audio_to_korean(
            chunk_path,
            source_locale=source_locale,
        )

        if "phrases" in result and result["phrases"]:
            srt_part, count = build_srt(
                result["phrases"], time_offset_ms=time_offset_ms
            )
            subtitle_count += count
            all_srt_parts.append(srt_part)

            # 다음 청크 오프셋 계산
            last_phrase = result["phrases"][-1]
            last_offset = last_phrase.get("offsetMilliseconds", 0)
            last_duration = last_phrase.get("durationMilliseconds", 0)
            time_offset_ms += last_offset + last_duration
        elif "combinedPhrases" in result and result["combinedPhrases"]:
            text = result["combinedPhrases"][0].get("text", "")
            srt_part = build_srt_from_combined(text)
            all_srt_parts.append(srt_part)
            time_offset_ms += CHUNK_DURATION_SEC * 1000

    if output_path is None:
        output_path = "output_korean_subtitle.srt"

    full_srt = "\n".join(all_srt_parts)

    print(f"[4/4] SRT 파일 저장: {output_path}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_srt)

    print(f"       → 완료! ({subtitle_count}개 자막 생성)")
    return output_path


# ---------------------------------------------------------------------------
# CLI 실행
# ---------------------------------------------------------------------------


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="YouTube 동영상의 음성을 추출하여 한글 자막(SRT)으로 변환합니다."
    )
    parser.add_argument("url", help="YouTube 동영상 URL")
    parser.add_argument(
        "--output", "-o",
        default="output_korean_subtitle.srt",
        help="출력 SRT 파일 경로 (기본: output_korean_subtitle.srt)",
    )
    parser.add_argument(
        "--source-locale", "-s",
        default="en-US",
        help="소스 오디오 언어 로케일 (기본: en-US, 예: ja-JP, ar-SA, fr-FR)",
    )

    args = parser.parse_args()

    if not RESOURCE_ID:
        print(
            "오류: AZURE_MAI_SPEECH_RESOURCE_ID 환경 변수를 .env 파일에 설정하세요.",
            file=sys.stderr,
        )
        sys.exit(1)

    srt_path = youtube_to_korean_srt(
        args.url,
        output_path=args.output,
        source_locale=args.source_locale,
    )
    print(f"\n자막 파일이 생성되었습니다: {srt_path}")


if __name__ == "__main__":
    main()
