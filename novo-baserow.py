import os
import requests

# Configurações
upload_url = "https://api.baserow.io/api/user-files/upload-file/"
table_url = "https://api.baserow.io/api/database/rows/table/391203/"
token = "uaDqFlR4y5cEt1oWbGrrSNUUAHjg6tq9"  # Substitua pelo seu token
file_field_id = "2973704"  # ID do campo onde o arquivo será salvo
directory = "partes_divididas"  # Pasta contendo os arquivos

def upload_file(file_path):
    """Faz o upload do arquivo e retorna o nome gerado do arquivo"""
    try:
        with open(file_path, "rb") as file:
            upload_response = requests.post(
                upload_url,
                headers={"Authorization": f"Token {token}"},
                files={"file": file}
            )
        
        if upload_response.status_code == 200:
            uploaded_file_data = upload_response.json()
            return uploaded_file_data["name"]  # Retorna o nome do arquivo gerado no upload
        else:
            print(f"Falha no upload de {file_path}. Status code: {upload_response.status_code}")
            print("Detalhes:", upload_response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição de {file_path}: {e}")
        return None


def create_row(file_name):
    """Cria uma linha na tabela do Baserow com o nome do arquivo"""
    data = {
        f"field_{file_field_id}": [{"name": file_name}]
    }
    table_response = requests.post(
        table_url,
        headers={
            "Authorization": f"Token {token}",
            "Content-Type": "application/json",
        },
        json=data
    )
    
    if table_response.status_code in (200, 201):
        print(f"Linha criada com sucesso para {file_name}!")
        print("Resposta da API:", table_response.json())
    else:
        print(f"Falha ao criar linha para {file_name}. Status code: {table_response.status_code}")
        print("Detalhes:", table_response.text)


def upload_files_from_directory(directory):
    """Itera sobre todos os arquivos na pasta e faz o upload"""
    # Verifica se a pasta existe
    if not os.path.isdir(directory):
        print(f"A pasta {directory} não existe.")
        return
    
    # Itera sobre todos os arquivos na pasta
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        
        # Verifica se é um arquivo .mp3
        if os.path.isfile(file_path) and file_name.endswith(".mp3"):
            print(f"Iniciando upload de {file_name}...")
            uploaded_file_name = upload_file(file_path)
            if uploaded_file_name:
                create_row(uploaded_file_name)


# Inicia o processo de upload
upload_files_from_directory(directory)




# Exemplo de uso
#arquivo_entrada = "videoplayback.mp3"
#api_url = "https://api.baserow.io"
#api_token = "uaDqFlR4y5cEt1oWbGrrSNUUAHjg6tq9"
#table_id = "391203"
#file_field_id = "2973704"  # Substituir pelo ID do campo de arquivo no Baserow
#dividir_e_subir_audio(arquivo_entrada, api_url, api_token, table_id, file_field_id)
