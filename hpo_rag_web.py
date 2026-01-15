# -*- coding: utf-8 -*-
import streamlit as st
import pickle

st.set_page_config(page_title="🩺 HPO RAG 500", layout="wide")
st.title("🩺 **HPO RAG 500 — 20 TESTS AUTOMATIQUES**")

# 🔥 CHARGE .PKL 500 HPO
@st.cache_data
def load_hpo_pkl():
    try:
        with open("hpo_google_production.pkl", "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        st.error("❌ **hpo_google_production.pkl MANQUANT!**")
        st.stop()

hpo_dict = load_hpo_pkl()
docs, labels, codes = hpo_dict['docs'], hpo_dict['labels'], hpo_dict['codes']
total_hpo = len(docs)

st.success(f"✅ **{total_hpo} HPO chargés (.PKL)**")

def search_hpo(query):
    if not query or not query.strip():
        return []
    
    query_lower = query.lower().strip()
    query_words = set(query_lower.split())
    
    scores = []
    seen = set()
    
    for i, doc in enumerate(docs):
        if codes[i] in seen:
            continue
            
        doc_lower = doc.lower()
        match_count = sum(1 for word in query_words if word in doc_lower)
        score = min(1.0, match_count / max(1, len(query_words)))
        
        if score > 0.1:
            scores.append((i, score))
            seen.add(codes[i])
    
    return sorted(scores, key=lambda x: x[1], reverse=True)[:3]

# 🔥 20 TESTS AUTOMATIQUES UNIQUES (15 originaux + 3 premiers manuels + 2 bonus)
st.markdown("─" * 90)
st.subheader("⚡ **20 TESTS AUTOMATIQUES (Cliquez!)**")

auto_tests = [
    # 10 ORIGINAUX AUTO
    "maux de tête", "douleur poitrine", "vertiges", 
    "vision floue", "nausées", "diarrhée",
    "polyurie", "fièvre", "douleur dos", "palpitations",
    
    # 🔥 3 PREMIERS MANUELS AJOUTÉS
    "toux grasse", "sueurs froides", "tête qui tourne",
    
    # 7 AUTRES DIVERS
    "douleur articulaire", "soif excessive", "selles liquides",
    "paupière tombante", "battements cœur", "fourmillements",
    "peau jaune"
]

auto_cols = st.columns(5)
for i, test in enumerate(auto_tests):
    with auto_cols[i%5]:
        if st.button(f"**{i+1}: {test.title()}**", use_container_width=True, key=f"auto_{i}"):
            results = search_hpo(test)
            st.session_state.results = results
            st.session_state.query = test
            st.session_state.test_type = "AUTO"
            st.rerun()

# 🔥 RECHERCHE LIBRE
st.markdown("─" * 90)
st.subheader("🔍 **RECHERCHE LIBRE**")
col1, col2 = st.columns([4,1])
free_query = col1.text_input("Tapez librement:", placeholder="Ex: fatigue extrême, yeux secs", key="free_input")

if col2.button("**🔍 LIBRE**", type="primary", key="libre_btn"):
    if free_query.strip():
        results = search_hpo(free_query)
        st.session_state.results = results
        st.session_state.query = free_query
        st.session_state.test_type = "LIBRE"
        st.rerun()

# 🔥 RÉSULTATS
st.markdown("─" * 90)
st.subheader("🏆 **RÉSULTATS**")

if 'results' in st.session_state and st.session_state.results:
    results = st.session_state.results
    query = st.session_state.query
    test_type = st.session_state.get('test_type', 'UNKNOWN')
    
    type_emoji = "⚡" if test_type == "AUTO" else "🔍"
    st.success(f"{type_emoji} **'{query}'** → {len(results)}/{total_hpo} HPO")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🎯 Score #1", f"{max([s for _,s in results]):.0%}")
    col2.metric("📊 Total HPO", f"{total_hpo:,}")
    col3.metric("🔍 Top 3", len(results))
    
    for rank, (i, score) in enumerate(results, 1):
        label, code, doc = labels[i], codes[i], docs[i]
        color = "🟢" if score > 0.5 else "🟡" if score > 0.25 else "🔴"
        
        st.markdown(f"""
        **{rank}°** `{code}` **{label}** {color} **{score:.0%}**
        📄 *{doc}*
        """)
        st.markdown("─" * 70)

    # BOUTON RESET
    if st.button("🔄 **RESET**", key="reset"):
        for key in ['results', 'query', 'test_type']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

else:
    st.info("👆 **Cliquez un des 20 tests ou LIBRE!**")

# RÉSUMÉ
with st.expander("📋 **20 TESTS DISPONIBLES**"):
    st.markdown("""
    **20 TESTS AUTO UNIQUES:**
    1. maux de tête → Headache
    2. douleur poitrine → Chest pain
    3. vertiges → Vertigo
    4. vision floue → Vision blurred
    5. nausées → Nausea
    6. diarrhée → Diarrhea
    7. polyurie → Polyuria
    8. fièvre → Fever
    9. douleur dos → Back pain
    10. palpitations → Tachycardia
    11. toux grasse → Cough *(manuel 1)*
    12. sueurs froides → Sweating *(manuel 2)*
    13. tête qui tourne → Dizziness *(manuel 3)*
    14. douleur articulaire → Arthralgia
    15. soif excessive → Polydipsia
    16. selles liquides → Diarrhea
    17. paupière tombante → Ptosis
    18. battements cœur → Tachycardia
    19. fourmillements → Paresthesia
    20. peau jaune → Jaundice
    """)

st.caption("🩺 **HPO RAG 500 — 20 TESTS AUTO UNIQUES ✅**")
