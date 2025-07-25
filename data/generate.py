import yaml
import os
import subprocess

# スクリプトと同じ階層に ver1.yaml, ver2.yaml がある想定
# 親ディレクトリに ver1/, ver2/ フォルダがあり、そこに .wav を出力

VOICE_NAME = "Samantha"
AUDIO_FORMAT = "wav"  # wav形式で出力


def synthesize_text(text, output_dir, output_prefix, voice_name=VOICE_NAME):
    """
    text を say で合成して一時AIFFを作成後、wavに変換して output_dir に保存
    """
    os.makedirs(output_dir, exist_ok=True)
    temp_aiff = os.path.join(output_dir, f"{output_prefix}.aiff")
    wav_path = os.path.join(output_dir, f"{output_prefix}.{AUDIO_FORMAT}")

    # say で aiff 作成
    say_cmd = ["say", "-o", temp_aiff]
    if voice_name:
        say_cmd += ["-v", voice_name]
    say_cmd.append(text)
    try:
        subprocess.run(say_cmd, check=True, capture_output=True, text=True)
        print(f"[OK] AIFF生成: {temp_aiff}")
    except subprocess.CalledProcessError as e:
        print(f"[Error] say コマンド失敗: {e.stderr}")
        return None

    # ffmpeg で wav に変換
    ff_cmd = [
        "ffmpeg", "-y",
        "-i", temp_aiff,
        "-vn",  # 動画なし
        "-acodec", "pcm_s16le",  # PCM 16-bit
        wav_path
    ]
    try:
        subprocess.run(ff_cmd, check=True, capture_output=True, text=True)
        print(f"[OK] WAV変換: {wav_path}")
        os.remove(temp_aiff)
    except subprocess.CalledProcessError as e:
        print(f"[Error] ffmpeg 失敗: {e.stderr}")
        return None
    except FileNotFoundError:
        print("[Error] ffmpeg が見つかりません。")
        return None

    return wav_path


def process_version(version):
    """
    version: 'ver1' など
    同じ階層の {version}.yaml を読み込み、
    一つ上の階層のフォルダ {version}/ に音声を出力
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(script_dir, f"{version}.yaml")
    output_dir = os.path.join(script_dir, os.pardir, version)

    # YAML 読み込み
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            examples = yaml.safe_load(f)
    except Exception as e:
        print(f"[Error] {yaml_path} の読み込み失敗: {e}")
        return

    # 各例文を合成
    for i, ex in enumerate(examples, start=1):
        prefix = f"{version}_{i:03d}"
        wav_file = synthesize_text(ex['english'], output_dir, prefix)
        if wav_file:
            print(f"Generated: {wav_file}")


if __name__ == '__main__':
    # ver1, ver2 を順に処理
    for ver in ['ver1', 'ver2']:
        print(f"--- Processing {ver} ---")
        process_version(ver)
