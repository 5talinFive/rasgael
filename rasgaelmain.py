import pandas as pd
from groq import Groq
import streamlit as st

# Leer datos de un archivo Excel en lugar de Google Sheets
data_df = pd.read_excel('DataCole.xlsx')

# Convertir datos a un diccionario
data_dict = {}
for index, row in data_df.iterrows():
    key = str(row[0]).strip().lower()
    value = str(row[1]).strip().lower()
    data_dict[key] = value

# Inicializa el cliente de Groq con el token desde los secretos
api_key = st.secrets["groq"]["api_key"]
client = Groq(api_key=api_key)

def get_relevant_info(query):
    query_lower = query.lower()
    relevant_info = []

    for k, v in data_dict.items():
        if any(word in k for word in query_lower.split()) or any(word in v for word in query_lower.split()):
            relevant_info.append(f"{k.capitalize()}: {v}")
    
    return "\n".join(relevant_info) if relevant_info else ""

def get_ia_response(messages):
    user_query = messages[-1]["content"].lower()
    
    relevant_context = ""
    if "colegio" in user_query or "rafael galeth" in user_query:
        relevant_context = get_relevant_info(user_query)
    
    context_message = {"role": "system", "content": f"Información relevante del Colegio Rafael Galeth:\n{relevant_context}\n"}
    
    completion = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=messages + [context_message],
        temperature=0.2,
        max_tokens=1024,
        stream=True,
    )
    
    response = "".join(chunk.choices[0].delta.content or "" for chunk in completion)
    return response

def chat():
    st.title("Chatea con RASGAEL")
    st.write("Bienvenido al chat con IA! Escribe 'salir' para terminar la conversación.")
    
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    
    def submit():
        user_input = st.session_state.user_input
        if user_input.lower() == 'salir':
            st.write("Gracias por chatear! ¡Adiós!")
            st.stop()
            
        st.session_state['messages'].append({"role": "user", "content": user_input})
        
        with st.spinner("Obteniendo respuesta..."):
            ia_response = get_ia_response(st.session_state['messages'])
            st.session_state['messages'].append({"role": "assistant", "content": ia_response})
        
        st.session_state.user_input = ""  # Limpiar el campo de entrada
    
    # Mostrar mensajes previos
    for message in st.session_state['messages']:
        role = "TU" if message["role"] == "user" else "RASGAEL"
        st.write(f"**{role}:** {message['content']}")
    
    # Crear el formulario
    with st.form(key='chat_form', clear_on_submit=True):
        st.text_input("TU:", key="user_input")
        submit_button = st.form_submit_button(label='Enviar', on_click=submit)

if __name__ == "__main__":
    chat()
