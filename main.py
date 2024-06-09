from pytube import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip
import os
import tempfile
import threading

def listarResolucoes(yt):
    streams = yt.streams.filter(file_extension='mp4', type='video').order_by('resolution')
    resolucoes = []
    for stream in streams:
        if stream.resolution not in resolucoes:
            resolucoes.append(stream.resolution)
    return resolucoes

def baixarStream(stream, output_path, filename):
    try:
        download_path = stream.download(output_path=output_path, filename=filename)
        return download_path
    except Exception as e:
        print(f"Erro ao baixar: {e}")
        return None

def converterMp3(audio_path, filename):
    try:
        mp3_path = os.path.join(os.path.expanduser('~'), 'Downloads', f"{filename}.mp3")
        audio_clip = AudioFileClip(audio_path)
        audio_clip.write_audiofile(mp3_path)
        audio_clip.close()
        print(f"Conversão completa! Arquivo MP3 salvo na pasta de Downloads.")
    except Exception as e:
        print(f"Erro durante a conversão: {e}")

def baixarVideo(url, filename):
    try:
        yt = YouTube(url)
        print("Título do vídeo:", yt.title)

        resolucoes = listarResolucoes(yt)
        print("Resoluções disponíveis:")
        for i, res in enumerate(resolucoes):
            print(f"{i + 1}. {res}")

        escolha = int(input("Escolha a resolução desejada (número): "))
        resolucao_escolhida = resolucoes[escolha - 1]

        # Obter streams de vídeo e áudio
        video_stream = yt.streams.filter(file_extension='mp4', type='video', resolution=resolucao_escolhida).first()
        audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()

        with tempfile.TemporaryDirectory() as temp_dir:
            video_thread = threading.Thread(target=baixarStream, args=(video_stream, temp_dir, f"{filename}_video.mp4"))
            audio_thread = threading.Thread(target=baixarStream, args=(audio_stream, temp_dir, f"{filename}_audio.mp4"))

            video_thread.start()
            audio_thread.start()

            video_thread.join()
            audio_thread.join()

            video_path = os.path.join(temp_dir, f"{filename}_video.mp4")
            audio_path = os.path.join(temp_dir, f"{filename}_audio.mp4")

            # Combina o vídeo e o áudio
            video_clip = VideoFileClip(video_path)
            audio_clip = AudioFileClip(audio_path)
            final_clip = video_clip.set_audio(audio_clip)

            final_path = os.path.join(os.path.expanduser('~'), 'Downloads', f"{filename}.mp4")
            final_clip.write_videofile(final_path, codec='libx264', audio_codec='aac')

        print("Download completo!")
        return final_path
    except Exception as e:
        print(f"Erro ao baixar o vídeo: {e}")
        return None

def baixarAudio(url, filename):
    try:
        yt = YouTube(url)
        print("Título do vídeo:", yt.title)
        audio_stream = yt.streams.filter(only_audio=True).first()
        download_path = baixarStream(audio_stream, os.path.join(os.path.expanduser('~'), 'Downloads'), f"{filename}.mp4")
        print("Download completo!")
        return download_path
    except Exception as e:
        print(f"Erro ao baixar o áudio: {e}")
        return None

if __name__ == "__main__":
    choice = input("Você deseja baixar o vídeo ou apenas o áudio? (video/audio): ").strip().lower()
    url = input("Digite o link do vídeo do YouTube: ")
    filename = input("Digite o nome desejado para o arquivo (sem extensão): ")

    if choice == "audio":
        audio_path = baixarAudio(url, filename)
        if audio_path:
            converterMp3(audio_path, filename)
    elif choice == "video":
        baixarVideo(url, filename)
    else:
        print("Escolha inválida. Por favor, escolha 'video' ou 'audio'.")