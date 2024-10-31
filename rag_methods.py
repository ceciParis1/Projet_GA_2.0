import requests
import streamlit as st

def get_documents_from_hal(keyword=None):
    base_url = "http://api.archives-ouvertes.fr/search/"
    url = f"{base_url}?q={keyword}&wt=json&fl=title_s,abstract_s,authFullName_s,producedDateY_i,docType_s"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json().get('response', {}).get('docs', [])
    else:
        st.error(f"Erreur lors de la requête: {response.status_code}")
        return []

# Fonction pour le streaming de la réponse LLM
def stream_llm_response(llm_stream, messages):
    response_message = ""
    for chunk in llm_stream.stream(messages):
        response_message += chunk.content
        yield chunk.content  # Renvoyer les chunks progressivement

    # Ajouter la réponse à l'historique des messages
    st.session_state.messages.append({"role": "assistant", "content": response_message})

# Fonction pour le streaming de la réponse LLM avec RAG
def stream_llm_rag_response(llm_stream, messages, documents):
    response_message = ""
    for chunk in llm_stream.stream(messages):
        response_message += chunk.content
        yield chunk.content  # Renvoyer les chunks progressivement

    # Ajouter la réponse à l'historique des messages
    st.session_state.messages.append({"role": "assistant", "content": response_message})

    # Ajouter les documents à l'historique des messages
    for doc in documents:
        st.session_state.messages.append({"role": "assistant", "content": f"**Titre:** {doc['title_s']}\n\n**Auteur(s):** {doc['authFullName_s']}\n\n**Résumé:** {doc['abstract_s']}\n\n**Date de publication:** {doc['producedDateY_i']}\n\n**Type de document:** {doc['docType_s']}"})
