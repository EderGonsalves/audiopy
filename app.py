from flask import Flask, request, render_template, send_from_directory
import os
import subprocess

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'partes_divididas'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def dividir_audio_com_ffmpeg(input_file, output_folder, max_size_mb=10):
    """
    Divide um arquivo de áudio em partes menores usando ffmpeg, sem carregar o arquivo inteiro na memória.
    """
    bitrate_kbps = 128  # Taxa de bits típica para MP3
    max_size_bytes = max_size_mb * 1024 * 1024
    max_duration_seconds = (max_size_bytes / (bitrate_kbps * 1000 / 8))  # max size in bytes to duration in seconds
    
    # Obtendo a duração total do arquivo de áudio
    result = subprocess.run(['ffmpeg', '-i', input_file, '-f', 'null', '-'], capture_output=True, text=True)
    duration_line = [line for line in result.stderr.splitlines() if "Duration" in line]
    duration_str = duration_line[0].split()[1]
    duration = sum(int(x) * 60 ** i for i, x in enumerate(reversed(duration_str.split(":"))))

    num_parts = 0
    for start_time in range(0, duration, int(max_duration_seconds)):
        output_file = os.path.join(output_folder, f"parte_{num_parts + 1}.mp3")
        subprocess.run(['ffmpeg', '-i', input_file, '-ss', str(start_time), '-t', str(max_duration_seconds), '-acodec', 'libmp3lame', '-ab', f'{bitrate_kbps}k', output_file])
        num_parts += 1

    return num_parts

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
        num_parts = dividir_audio_com_ffmpeg(file_path, app.config['OUTPUT_FOLDER'])
        
        # Retornar o resultado para o navegador
        return (
            f"Áudio dividido em {num_parts} partes. Verifique a pasta: {app.config['OUTPUT_FOLDER']}"
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
