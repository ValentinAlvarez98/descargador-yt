import os
import yt_dlp
import streamlit as st
import tempfile

COOKIES_YOUTUBE = st.secrets["COOKIES_YOUTUBE"]

class YouTubeDownloader:
    def __init__(self, url):
        self.url = url
        self.info_dict = None
        self.file_path = None

    def fetch_video_info(self):
        # Crear un archivo temporal para las cookies
        with tempfile.NamedTemporaryFile(delete=False) as temp_cookie_file:
            temp_cookie_file.write(COOKIES_YOUTUBE.encode('utf-8'))
            temp_cookie_file_name = temp_cookie_file.name

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'cookies': temp_cookie_file_name 
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                self.info_dict = ydl.extract_info(self.url, download=False)
                return True
            except Exception as e:
                st.error(f"Error al obtener información del video: {e}")
                return False
            finally:
                os.remove(temp_cookie_file_name)

    def show_info(self):
        if self.info_dict:
            st.write(f"**Título:** {self.info_dict.get('title')}")
            st.write(f"**Autor:** {self.info_dict.get('uploader')}")
            st.write(f"**Duración:** {self.info_dict.get('duration')} segundos")

    def download(self):
        progress_bar_placeholder = st.empty()

        progress_bar_placeholder.progress(0)

        with tempfile.NamedTemporaryFile(delete=False) as temp_cookie_file:
            temp_cookie_file.write(COOKIES_YOUTUBE.encode('utf-8'))
            temp_cookie_file_name = temp_cookie_file.name

        def progress_hook(d):
            if d['status'] == 'downloading':
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes', 1)
                percent = downloaded / total
                progress_bar_placeholder.progress(percent)

        ydl_opts = {
            'format': 'best',
            'outtmpl': '%(title)s.%(ext)s',
            'cookies': temp_cookie_file_name, 
            'progress_hooks': [progress_hook], 
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(self.url, download=True)
            self.file_path = ydl.prepare_filename(info)

        st.success("¡Video disponible para la descarga!")

        os.remove(temp_cookie_file_name)

        return self.file_path

if __name__ == "__main__":
    st.title("Descargador de videos de YouTube")
    url = st.text_input("Ingresa la URL del video")

    if url:
        downloader = YouTubeDownloader(url)
        if downloader.fetch_video_info():
            downloader.show_info()
            if st.button("Cargar video"):
                file_path = downloader.download()
                if file_path:
                    with open(file_path, "rb") as file:
                        st.download_button(
                            label="Descargar Video",
                            data=file,
                            file_name=os.path.basename(file_path),
                            mime="video/mp4"
                        )
                    os.remove(file_path)
