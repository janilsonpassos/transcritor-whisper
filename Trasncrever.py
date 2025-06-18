import streamlit as st
import whisper
import os
import subprocess
import glob
from datetime import datetime

# Função para dividir o áudio
def dividir_audio(nome_arquivo, duracao_segundos=300):
    subprocess.call([
        "ffmpeg", "-i", nome_arquivo, "-f", "segment",
        "-segment_time", str(duracao_segundos), "-c", "copy", "parte_%03d.mp3"
    ])

# Função para transcrever com Whisper
def transcrever_partes(modelo="base"):
    partes = sorted(glob.glob("parte_*.mp3"))
    transcricoes = []

    model = whisper.load_model(modelo)

    for parte in partes:
        st.write(f"🔊 Transcrevendo {parte}...")
        resultado = model.transcribe(parte, language="pt")
        texto = resultado["text"]
        nome_txt = parte.replace(".mp3", ".txt")
        with open(nome_txt, "w", encoding="utf-8") as f:
            f.write(texto)
        transcricoes.append((parte, texto))

    return transcricoes

# Função para juntar em um único arquivo
def juntar_transcricoes():
    arquivos_txt = sorted(glob.glob("parte_*.txt"))
    final_path = "transcricao_final.txt"

    with open(final_path, "w", encoding="utf-8") as final:
        for nome_txt in arquivos_txt:
            with open(nome_txt, "r", encoding="utf-8") as f:
                final.write(f"### {nome_txt} ###\n")
                final.write(f.read() + "\n\n")
    
    return final_path

# Função para limpar os arquivos temporários
def limpar_arquivos():
    for f in glob.glob("parte_*.mp3") + glob.glob("parte_*.txt"):
        os.remove(f)

# Interface do Streamlit
st.title("🎙️ Transcritor de Áudio com Whisper")
st.write("Envie um arquivo de áudio para dividir, transcrever e juntar automaticamente.")

arquivo = st.file_uploader("Selecione um arquivo de áudio (MP3, MP4, WAV)", type=["mp3", "mp4", "wav", "m4a"])

modelo = st.selectbox("Escolha o modelo de transcrição", ["tiny", "base", "small", "medium", "large"], index=1)

if arquivo is not None:
    # Salvar arquivo
    nome_arquivo = f"audio_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
    with open(nome_arquivo, "wb") as f:
        f.write(arquivo.getbuffer())
    st.success(f"Arquivo salvo como: {nome_arquivo}")

    if st.button("🚀 Iniciar Transcrição"):
        st.write("🔧 Dividindo o áudio...")
        dividir_audio(nome_arquivo)

        st.write("🧠 Carregando modelo e transcrevendo...")
        transcricoes = transcrever_partes(modelo)

        st.write("📄 Juntando todas as transcrições...")
        final = juntar_transcricoes()

        with open(final, "r", encoding="utf-8") as f:
            st.download_button("📥 Baixar Transcrição Final", f, file_name=final)

        st.success("✅ Transcrição concluída!")

    if st.button("🗑️ Limpar arquivos temporários"):
        limpar_arquivos()
        st.success("Arquivos removidos com sucesso!")
