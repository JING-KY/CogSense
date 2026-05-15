# CogSense - Passive Cognitive Monitoring System

A proof-of-concept system for passive cognitive health monitoring through automated analysis of naturalistic family dialogue.

## 🌐 Live Demo

👉 **[Try CogSense Online](你的Streamlit链接，稍后填写)**

## 📖 Overview

CogSense demonstrates the feasibility of detecting cognitive decline markers in everyday conversations using:
- Large Language Model (LLM) for synthetic dialogue generation
- Rule-based linguistic feature extraction
- Interpretable multi-dimensional cognitive scoring
- Interactive web-based visualization

## 🎯 Features

- 🎙️ **Real-time Monitoring**: Simulated dialogue monitoring with event detection
- 📊 **Multi-dimensional Analysis**: Five cognitive dimensions (Memory, Planning, Recall, Coherence, Temporal Orientation)
- 📈 **Interactive Dashboard**: Radar charts, trend lines, and feature tables
- 📄 **Clinical Reports**: Automated generation of structured assessment reports

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Anaconda (recommended)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/你的用户名/CogSense.git
cd CogSense
```

2. Create and activate conda environment:

```bash
conda create -n cogsense python=3.11 -y
conda activate cogsense
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up API credentials:

Create a `.streamlit/secrets.toml` file (for local development):

```toml
OPENAI_API_KEY = "your-api-key-here"
OPENAI_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL_NAME = "qwen-plus"
```

Or set environment variables:

```bash
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export MODEL_NAME="qwen-plus"
```

5. Run the application:

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
CogSense/
├── app.py                    # Main Streamlit application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── modules/                  # Core functional modules
│   ├── dialogue_generator.py
│   ├── linguistic_analyzer.py
│   ├── cognitive_scorer.py
│   ├── database_manager.py
│   └── report_generator.py
├── utils/                    # Utility functions
│   ├── prompts.py
│   └── visualization.py
├── data/                     # Data storage
│   └── dialogues.json
├── database/                 # SQLite database
└── assets/                   # Static assets
```

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| Frontend | Streamlit |
| Backend | Python 3.11 |
| Database | SQLite |
| Visualization | Plotly |
| NLP | jieba (Chinese word segmentation) |
| LLM | Alibaba Qwen (via OpenAI-compatible API) |

## 📊 Dataset

The system uses synthetically generated dialogue data created via prompt engineering with a large language model. The corpus includes:

- 150 dialogues (50 per cognitive group)
- 3 cognitive status groups: Healthy Controls (HC), Mild Cognitive Impairment (MCI), Early Dementia (ED)
- 8 conversational scenarios
- ~36 turns per dialogue

## 🔬 Methodology

### Linguistic Features (8)

- Vocabulary Richness (Type-Token Ratio)
- Vague Pronoun Ratio
- Repair Frequency
- Repetition Rate
- Coherence Score
- Temporal Confusion
- Average Utterance Length
- Filler Word Ratio

### Cognitive Dimensions (5)

| Dimension | Weight |
| :--- | :---: |
| Memory | 25% |
| Planning | 20% |
| Recall | 20% |
| Coherence | 20% |
| Temporal Orientation | 15% |

### Risk Classification

- **Low Risk**: Total score ≥ 80
- **Medium Risk**: Total score 60-79
- **High Risk**: Total score < 60

## ⚠️ Limitations

- Uses synthetic rather than authentic clinical dialogue data
- Rule-based scoring has performance ceiling compared to ML approaches
- Lacks clinical validation with real patients
- Currently supports Mandarin Chinese only
- Text-based input only (ASR integration pending)

## 🔮 Future Directions

- Validation with authentic clinical dialogue data
- Integration with automatic speech recognition (ASR)
- Multimodal analysis (acoustic + visual features)
- Longitudinal validation studies
- Cross-linguistic adaptation

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

This project was developed as part of a course assignment. Special thanks to the course instructors (Prof. Liu) and domain experts who provided feedback.

## 📧 Contact

For questions or collaboration inquiries, please open an issue on GitHub.

## ⚖️ Ethical Considerations

This is a research prototype and should **NOT** be used for clinical diagnosis. Any real-world deployment must address:

- Privacy and data protection
- Informed consent
- Algorithmic bias
- False positive/negative impacts
- Regulatory compliance

## 👤 Author

**JING Kaiyuan**
- GitHub: [@JING-KY](https://github.com/JING-KY)
- Email: jingky@life.hkbu.edu.hk
- Institution: HKBU
