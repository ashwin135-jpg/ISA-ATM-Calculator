import streamlit as st
import streamlit.components.v1 as components

def run():
    st.set_page_config(layout="wide")

    DESIGNER_HTML = """
    <!doctype html>
    <html>
      <head>
        <style>
          body { background:#070A12; color:#EAF0FF; }
        </style>
      </head>
      <body>
        <h1>ISA Aircraft Designer</h1>
        <p>Futuristic UI goes here</p>

        <script>
          // JS that calls FastAPI backend
          console.log("ISA Designer loaded");
        </script>
      </body>
    </html>
    """

    components.html(
        DESIGNER_HTML,
        height=900,
        scrolling=False
    )
