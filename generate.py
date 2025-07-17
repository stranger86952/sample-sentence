import yaml
import os
import subprocess

AUDIO_DIR = "audio"

def synthesize_text_with_say(text, output_prefix, voice_name="Samantha"):
    os.makedirs(AUDIO_DIR, exist_ok=True)
    temp_aiff_path = os.path.join(AUDIO_DIR, f"{output_prefix}.aiff")
    mp3_path = os.path.join(AUDIO_DIR, f"{output_prefix}.mp3")

    say_command = ["say", "-o", temp_aiff_path]
    if voice_name:
        say_command.extend(["-v", voice_name])
    say_command.append(text)

    try:
        subprocess.run(say_command, check=True, capture_output=True, text=True)
        print(f"一時AIFF音声 '{os.path.basename(temp_aiff_path)}' を生成しました。")
    except subprocess.CalledProcessError as e:
        print(f"エラー: sayコマンドの実行に失敗しました: {e.stderr}")
        print(f"テキスト: {text}")
        print(f"コマンド: {' '.join(say_command)}")
        return None

    ffmpeg_command = ["ffmpeg", "-i", temp_aiff_path, "-vn", "-acodec", "libmp3lame", "-q:a", "2", mp3_path]

    try:
        subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
        print(f"MP3音声 '{os.path.basename(mp3_path)}' に変換しました。")
        os.remove(temp_aiff_path)
        print(f"一時AIFFファイル '{os.path.basename(temp_aiff_path)}' を削除しました。")
    except subprocess.CalledProcessError as e:
        print(f"エラー: FFmpegの実行に失敗しました: {e.stderr}")
        print(f"コマンド: {' '.join(ffmpeg_command)}")
        return None
    except FileNotFoundError:
        print("エラー: FFmpegが見つかりません。FFmpegがインストールされ、パスが通っていることを確認してください。")
        return None
    return mp3_path


def generate_html_from_yaml_with_audio(yaml_file, output_html_file):
    try:
        with open(yaml_file, 'r', encoding='utf-8') as f:
            examples = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"エラー: {yaml_file} が見つかりません。")
        return
    except yaml.YAMLError as e:
        print(f"エラー: YAMLファイルの解析に失敗しました: {e}")
        return

    html_content = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>英文・和訳 対訳集 (英文音声付き)</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>英文・和訳 対訳集 (英文音声付き)</h1>
    <div class="container">
    """

    english_voice = "Samantha"

    for i, example in enumerate(examples):
        output_prefix = f"en_{i+1:03d}"
        mp3_audio_path = synthesize_text_with_say(example['english'], output_prefix, voice_name=english_voice)

        english_audio_tag = f'<audio controls src="{AUDIO_DIR}/{output_prefix}.mp3"></audio>' if mp3_audio_path else ''

        html_content += f"""
        <div class="example-pair">
            <div class="english">
                <span class="number">{i+1}.</span> {example['english']}
                {english_audio_tag}
            </div>
            <div class="japanese">
                {example['japanese']}
            </div>
        </div>
        """

    html_content += """
    </div>
</body>
</html>
    """

    with open(output_html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"'{output_html_file}' が正常に生成されました。")
    print(f"MP3音声ファイルは '{AUDIO_DIR}/' ディレクトリに保存されています。")


if __name__ == "__main__":
    script_dir = os.path.dirname(__file__)
    yaml_path = os.path.join(script_dir, 'data.yaml')
    html_path = os.path.join(script_dir, 'index.html')
    generate_html_from_yaml_with_audio(yaml_path, html_path)
