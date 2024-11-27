from flask import Flask, request, render_template, send_from_directory
import os
from pydub import AudioSegment
import subprocess

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'partes_divididas'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def dividir_audio_em_partes(input_file, output_folder, max_size_mb=10):
    """
    Divide um arquivo de áudio longo em partes menores do que max_size_mb.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    audio = AudioSegment.from_file(input_file)
    bitrate_kbps = 128  # Taxa de bits típica para MP3
    bytes_per_second = (bitrate_kbps * 1000) // 8
    max_size_bytes = max_size_mb * 1024 * 1024
    max_duration_ms = (max_size_bytes / bytes_per_second) * 1000

    num_parts = 0
    for i in range(0, len(audio), int(max_duration_ms)):
        part = audio[i:i + int(max_duration_ms)]
        part_file = os.path.join(output_folder, f"parte_{num_parts + 1}.mp3")
        part.export(part_file, format="mp3", bitrate=f"{bitrate_kbps}k")
        num_parts += 1

    return num_parts

def run_script(script_path):
    """
    Executa outro script Python após a execução de um arquivo.
    """
    try:
        result = subprocess.run(['python', script_path], check=True, capture_output=True, text=True)
        return f"Script {script_path} executado com sucesso!\nSaída:\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Erro ao executar o script {script_path}.\nErro:\n{e.stderr}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'audio_file' not in request.files:
            return "Nenhum arquivo enviado", 400
        
        audio_file = request.files['audio_file']
        if audio_file.filename == '':
            return "Nenhum arquivo selecionado", 400

        # Salvar o arquivo enviado
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_file.filename)
        audio_file.save(file_path)

        # Dividir o áudio em partes
        num_parts = dividir_audio_em_partes(file_path, app.config['OUTPUT_FOLDER'])
        
        # Executar o script novo-baserow.py
        script_path = "novo-baserow.py"  # Caminho para o script a ser executado
        script_output = run_script(script_path)

        # Retornar o resultado para o navegador
        return (
            f"Áudio dividido em {num_parts} partes. Verifique a pasta: {app.config['OUTPUT_FOLDER']}<br>"
            f"Saída do script <b>{script_path}</b>:<br><pre>{script_output}</pre>"
        )

    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    """
    Permite o download de partes divididas do áudio.
    """
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    # Configurar a porta do serviço no Render
    port = int(os.environ.get('PORT', 10000))  # Usar a porta da variável de ambiente ou 10000 por padrão
    app.run(host='0.0.0.0', port=port, debug=True)
