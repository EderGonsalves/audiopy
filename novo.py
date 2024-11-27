import os
from pydub import AudioSegment
import subprocess

def dividir_audio_em_partes(input_file, output_folder, max_size_mb=10):
    """
    Divide um arquivo de áudio longo em partes menores do que max_size_mb.
    
    :param input_file: Caminho do arquivo de áudio de entrada.
    :param output_folder: Pasta onde as partes divididas serão salvas.
    :param max_size_mb: Tamanho máximo de cada parte em MB (padrão: 20 MB).
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Carregar o áudio
    audio = AudioSegment.from_file(input_file)
    
    # Estimativa do tamanho de áudio por segundo em MB (taxa de bits típica de 128 kbps para MP3)
    bitrate_kbps = 128  # Taxa de bits típica para MP3
    bytes_per_second = (bitrate_kbps * 1000) // 8
    max_size_bytes = max_size_mb * 1024 * 1024
    max_duration_ms = (max_size_bytes / bytes_per_second) * 1000  # Duração máxima por parte em ms

    # Dividir o áudio em partes
    num_parts = 0
    for i in range(0, len(audio), int(max_duration_ms)):
        part = audio[i:i + int(max_duration_ms)]
        part_file = os.path.join(output_folder, f"parte_{num_parts + 1}.mp3")
        part.export(part_file, format="mp3", bitrate=f"{bitrate_kbps}k")
        print(f"Parte {num_parts + 1} salva em: {part_file}")
        num_parts += 1

    print(f"Divisão concluída. Total de partes: {num_parts}")

# Exemplo de uso
arquivo_entrada = "videoplayback.mp3"  # Caminho para o arquivo de áudio de entrada
pasta_saida = "partes_divididas"     # Pasta onde as partes serão salvas
dividir_audio_em_partes(arquivo_entrada, pasta_saida)

def run_script(script_path):
    """Executa outro script Python após a execução de um arquivo"""
    try:
        result = subprocess.run(['python', script_path], check=True, capture_output=True, text=True)
        print(f"Script {script_path} executado com sucesso!")
        print("Saída:", result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o script {script_path}.")
        print("Erro:", e.stderr)


# Exemplo de uso
script_path = "novo-baserow.py"  # Caminho para o segundo script
run_script(script_path)
