# 🫀 CardioPredict AI

> **Plateforme d'aide à la décision cardiovasculaire propulsée par AutoML et IA générative**
📺 **[Voir la démo vidéo sur YouTube](https://youtube.com/watch?v=VOTRE-VIDEO-ID)**
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io)
[![PyCaret](https://img.shields.io/badge/PyCaret-3.x-orange.svg)](https://pycaret.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## ⚠️ Version prototype

**Cette version publique est une version initiale et démonstrative** de CardioPredict AI, construite avec **Streamlit** pour faciliter le prototypage rapide et la démonstration des concepts AutoML appliqués au domaine médical.

Elle a été développée dans le cadre d'un projet d'école d'ingénieur pour démontrer comment **l'AutoML démocratise le machine learning** dans le secteur de la santé, permettant aux professionnels médicaux non-techniciens de prototyper des outils prédictifs cliniques.

> 🏢 **Une version propriétaire avancée**, conteneurisée sous **Docker** avec une architecture microservices, des modèles spécialisés cardiovasculaires et une conformité réglementaire , est en développement séparé pour un déploiement clinique en production.

---

## 🎯 Concept

CardioPredict AI permet à un cardiologue, une infirmière ou un personnel clinique de :

1. **Charger** des données patient (CSV ou saisie manuelle)
2. **Entraîner** automatiquement le meilleur modèle de prédiction parmi 15+ algorithmes (sans une seule ligne de code)
3. **Prédire** le risque cardiovasculaire de chaque patient avec un système d'alertes 🔴 🟡 🟢
4. **Comprendre** les résultats grâce à une interprétation en langage médical générée par GPT-4o
5. **Générer** un rapport PDF clinique professionnel
6. **Interagir** avec l'application en français, anglais ou darija marocaine — y compris à la voix

## 🧠 Architecture

```
┌─────────────────┐
│   Streamlit UI  │  ← Interface multilingue (FR / AR / EN)
└────────┬────────┘
         │
┌────────▼────────┐
│   GPT-4o Brain  │  ← Compréhension du langage naturel + Whisper voice
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────────┐
│PyCaret │ │GPT-4o Médical│  ← AutoML + Interprétation clinique
└────┬───┘ └──────┬───────┘
     │            │
     └─────┬──────┘
           ▼
    ┌──────────────┐
    │Session State │  ← Mémoire de l'app
    └──────┬───────┘
           │
    ┌──────▼───────────────────────┐
    │ Sorties: Alertes, Dashboards,│
    │ Rapports PDF cliniques       │
    └──────────────────────────────┘
```
## ✨ Fonctionnalités principales

- 🤖 **AutoML avec PyCaret** — comparaison automatique de 15+ algorithmes (Random Forest, XGBoost, LightGBM, SVM, etc.)
- 💬 **Chatbot médical** propulsé par OpenAI GPT-4o avec function calling
- 🎙️ **Entrée vocale** via OpenAI Whisper (FR / AR / EN)
- 🌍 **Multilingue** : français, darija marocaine, anglais
- 🔬 **Phénotypage des patients** par K-Means clustering
- 📊 **Visualisations interactives** (Plotly, SHAP)
- 🩺 **Interprétation médicale** automatique en langage clinique
- 📄 **Rapports PDF cliniques** professionnels (8 pages)
- 🏥 **Mode clinique production** : patient unique, batch, suivi wearable
- 💾 **Sauvegarde du modèle** entraîné pour déploiement

---

## 🚀 Démarrage rapide

### Prérequis

- **Python 3.11** (PyCaret ne supporte pas Python 3.12+)
- Une clé API **OpenAI** ([obtenir une clé](https://platform.openai.com/api-keys))

### Installation

```bash
# 1. Cloner le repo
git clone https://github.com/VOTRE-USERNAME/cardiopredict-ai.git
cd cardiopredict-ai

# 2. Créer un environnement virtuel Python 3.11
python -m venv venv

# 3. Activer le venv
# Sur Windows :
venv\Scripts\activate.bat
# Sur Mac/Linux :
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Configurer la clé OpenAI
mkdir -p .streamlit
echo 'OPENAI_API_KEY = "sk-votre-cle-ici"' > .streamlit/secrets.toml

# 6. Lancer l'application
streamlit run app.py
```

L'app s'ouvre automatiquement dans votre navigateur sur `http://localhost:8501`.

---


## 🗂️ Structure du projet

```
cardiopredict-ai/
├── app.py                    # Point d'entrée Streamlit
├── automl/
│   ├── engine.py             # Wrapper PyCaret (CardiacAutoMLEngine)
│   └── preprocessor.py       # Préparation des données
├── chatbot/
│   ├── agent.py              # Logique OpenAI function calling
│   ├── voice.py              # Whisper transcription
│   ├── medical_interpreter.py# Interprétation médicale par LLM
│   └── prompts.py            # System prompts
├── reports/
│   ├── pdf_generator.py      # Génération PDF (ReportLab)
│   └── report_builder.py     # Builder de rapport
├── ui/
│   ├── components.py         # Composants Streamlit custom
│   └── charts.py             # Graphiques Plotly
├── i18n/
│   └── translations.py       # Traductions FR/AR/EN
├── data/
│   └── sample_heart.csv      # Dataset démo (UCI Heart Disease)
├── models/
│   └── cardiac_model.pkl     # Modèle pré-entraîné (généré)
├── requirements.txt
└── README.md
```
## ⚖️ Avertissement médical

**CardioPredict AI est un outil d'aide à la décision et un prototype académique.** Les prédictions générées :

- ❌ **Ne sont pas un diagnostic médical**
- ❌ **Ne remplacent pas le jugement clinique**
- ❌ **Ne sont pas certifiées CE médical / FDA**
- ✅ **Doivent être interprétées par un professionnel de santé qualifié**

L'utilisation de cet outil dans un cadre clinique réel nécessiterait une validation prospective, une certification réglementaire (CE médical, RGPD, HIPAA) et une supervision médicale.

---

## 🛣️ Roadmap

- [x] Prototype Streamlit avec PyCaret
- [x] Multilingue FR/AR/EN
- [x] Entrée vocale Whisper
- [x] Génération de rapports PDF
- [x] Mode clinique (patient unique / batch / wearable)
- [ ] **Version Docker propriétaire** (en développement séparé)
- [ ] Intégration dossier patient (HL7/FHIR)
- [ ] Modèles spécialisés cardiovasculaires (Cox, Survival Analysis)
- [ ] Validation clinique prospective
- [ ] Certification CE médical

---

## 🙏 Remerciements

- **[PyCaret](https://pycaret.org)** — Librairie AutoML open source (MIT) qui constitue le cœur de notre moteur de prédiction
- **[OpenAI](https://openai.com)** — Modèles GPT-4o et Whisper utilisés via leur API pour l'interprétation médicale et la transcription vocale
- **[Streamlit](https://streamlit.io)** — Framework Python utilisé pour l'interface utilisateur et le prototypage rapide
- **[UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/45/heart+disease)** — Heart Disease Dataset utilisé pour l'entraînement et la démonstration

---

### À propos de la version propriétaire

La version Docker propriétaire en développement explore plusieurs pistes d'extension :

- **Spécialisation médicale de PyCaret** : ajout de métriques cliniques (sensibilité, spécificité, PPV, NPV, NNS) et de modèles de survie (Cox, Random Survival Forest) particulièrement adaptés au domaine cardiovasculaire
- **Architecture microservices conteneurisée** sous Docker pour un déploiement clinique scalable
- **Conformité réglementaire** : conception orientée RGPD, hébergement souverain envisagé, et préparation à la certification CE médical
- **Intégration aux systèmes hospitaliers** via les standards HL7/FHIR

> Cette version pro reste fermée et n'est pas distribuée publiquement.
---

## 📜 Licence

Ce projet est distribué sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 👤 Auteur

**MOHAMED DOUAS** — Étudiant ingénieur(engineering IS and digital transformation) — Projet académique 2026

> 💡 La version Docker propriétaire avancée pour usage clinique professionnel n'est pas open source. Pour toute demande de collaboration ou de licence commerciale, contactez l'auteur.