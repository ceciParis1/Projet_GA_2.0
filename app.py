import streamlit as st
import os
import dotenv
import uuid
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from rag_methods import (
    get_documents_from_hal,
    stream_llm_response,
    stream_llm_rag_response,
)

dotenv.load_dotenv()

# Configuration de la page avec des éléments visuels
st.set_page_config(
    page_title="Recherche et Analyse de Documents Académiques",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Titre principal avec style
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Recherche et Analyse de Documents Académiques</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# Ajout de texte d'introduction
st.markdown("""
<div style='text-align: center;'>
    <p>Utilisez cette application pour trouver des documents académiques selon un mot-clé et les analyser grâce à un modèle de langage.</p>
    <p style='color: #6c757d;'>Propulsé par GPT-4 et HAL</p>
</div>
""", unsafe_allow_html=True)

# Insérer directement la clé API ici (c'est temporaire et non recommandé pour la production)
api_key = "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"

# Vérifier si la clé est bien présente
if not api_key:
    st.error("Clé API OpenAI manquante. Assurez-vous de l'insérer correctement dans le fichier app.py.")
else:
    st.success("Clé API OpenAI chargée avec succès.")

# Initialiser le modèle OpenAI
llm_stream = ChatOpenAI(
    api_key=api_key,  # Utiliser la clé API ici
    model_name="gpt-4",
    temperature=0.7,
    streaming=True,
)

# Initialisation de la session
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bienvenue ! Je peux vous aider à trouver des documents académiques et à en discuter ou les analyser."}
    ]

# Affichage des messages de la session avec mise en forme
for message in st.session_state.messages:
    role = "Utilisateur" if message["role"] == "user" else "Assistant"
    color = "#3498db" if message["role"] == "user" else "#2ecc71"
    st.markdown(f"<div style='background-color:{color};padding:10px;border-radius:10px;color:white;'><strong>{role}:</strong><br>{message['content']}</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# Saisie d'un nouveau message par l'utilisateur
if prompt := st.chat_input("Votre message"):
    # Vérification si le message contient un mot-clé pour la recherche de documents
    if "mot-clé" in prompt.lower():
        # Extraire le mot-clé du message
        keyword = prompt.split("mot-clé")[-1].strip()
        st.session_state.messages.append({"role": "user", "content": f"Recherche de documents sur le mot-clé '{keyword}'."})

        # Recherche de documents via HAL
        documents = get_documents_from_hal(keyword=keyword)

        if documents:
            for doc in documents:
                with st.chat_message("assistant"):
                    st.markdown(f"**Titre:** {doc['title_s']}\n\n**Auteur(s):** {doc['authFullName_s']}\n\n**Résumé:** {doc['abstract_s']}\n\n**Date de publication:** {doc['producedDateY_i']}\n\n**Type de document:** {doc['docType_s']}")
                    st.session_state.messages.append({"role": "assistant", "content": f"**Titre:** {doc['title_s']}\n\n**Auteur(s):** {doc['authFullName_s']}\n\n**Résumé:** {doc['abstract_s']}\n\n**Date de publication:** {doc['producedDateY_i']}\n\n**Type de document:** {doc['docType_s']}"})

            # Utilisation du LLM pour fournir une analyse du document
            with st.chat_message("assistant"):
                user_prompt = f"Voici un document sur {keyword}. Peux-tu en faire une analyse ?"
                messages = [HumanMessage(content=user_prompt)]

                full_response = ""
                placeholder = st.empty()  # Créer un espace réservé pour accumuler et afficher les résultats

                for chunk in stream_llm_rag_response(llm_stream, messages, documents):
                    full_response += chunk.content  # Ajout du texte sans espaces supplémentaires
                    # Ajout d'une mise en forme du document avec deux sauts de ligne pour séparer les strophes
                    formatted_text = full_response.replace('\n', '  \n')
                    placeholder.markdown(formatted_text)  # Affichage du texte accumulé progressivement avec la bonne mise en forme

                st.session_state.messages.append({"role": "assistant", "content": full_response})
        else:
            st.warning("Aucun document trouvé avec les critères spécifiés.")
            st.session_state.messages.append({"role": "assistant", "content": "Aucun document trouvé avec les critères spécifiés."})
    else:
        # Enregistrement du message utilisateur
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Réponse du LLM
        with st.chat_message("assistant"):
            # Vérification que le prompt n'est pas vide
            if prompt:
                messages = [HumanMessage(content=prompt)]
                full_response = ""
                placeholder = st.empty()  # Espace réservé pour la réponse

                # Itération sur le générateur pour afficher la réponse du LLM
                for chunk in stream_llm_response(llm_stream, messages):
                    full_response += chunk  # Ajout du chunk sans espace supplémentaire
                    # Ajout de la mise en forme avec des retours à la ligne appropriés
                    formatted_text = full_response.replace('\n', '  \n')
                    placeholder.markdown(formatted_text)  # Affichage du chunk dans l'interface

                # Enregistrement de la réponse complète dans l'état de session
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.warning("Veuillez saisir un message avant de soumettre.")
