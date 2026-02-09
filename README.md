# 🛡️ Bharat Guardian AI
**Empowering India's growth through secure, multimodal AI—from the farm to the courtroom.**

## 📝 Abstract
Bharat Guardian AI leverages the state-of-the-art **Gemini 3 Flash** model to transform complex legal and financial data into actionable intelligence. Unlike traditional LLMs, Gemini 3 Flash is specifically utilized here for its high-speed multimodal reasoning and massive context window, which are central to the three pillars of this application.

In **Piggy AI**, we utilize Gemini’s native ability to process real-time web data and voice-to-text inputs. This allows the model to act as a localized financial advisor, cross-referencing user income levels with live 2026 government schemes. In **Vantage Juris**, the model's advanced long-context understanding is critical. It analyzes thousands of words from landmark judgments—like *Kharak Singh vs State of UP*—to architect trial strategies and audit contracts for hidden scams with "Reasoning Audit" transparency. Finally, **Vision-to-Sheet** uses Gemini’s sophisticated Pixel-Sharing method. Instead of simple OCR, the model analyzes the spatial layout of documents to extract structured tabular data with near-perfect accuracy.

By integrating Gemini 3, the application moves beyond static automation; it provides a "Guardian" that can see, hear, and reason through the specific socio-economic lens of an Indian citizen, making high-level legal and financial expertise accessible to everyone.

---

## 🛠️ Tech Stack
* **Language:** Python
* **Web Framework:** Streamlit
* **Core AI:** Gemini 3 Flash (Multimodal Reasoning)
* **Creative Engine:** Nano Banana (Image Generation)
* **Search Intelligence:** DuckDuckGo Search (DDGS)
* **Data Handling:** Pandas & NumPy
* **Document Parsing:** PyPDF2 & pdfplumber
* **Visualization:** Plotly
* **Translation:** Deep Translator API

---

## ✨ Key Capabilities
* **📸 Vision-to-Sheet:** Spatial layout analysis to convert physical documents into clean digital spreadsheets using the Pixel-Sharing method.
* **⚖️ Vantage Juris:** Deep-dive legal analytics, precedent scouting, and trial strategy architecture with long-context reasoning.
* **🐷 Piggy AI:** Real-time financial scouting for localized government schemes, GST compliance, and voice-activated assistance.
* **🌐 Regional Sovereignty:** Full UI and output support for Hindi, Marathi, and other regional languages via dynamic translation.
* **🎙️ Voice-First Design:** Integrated speech-to-text for hands-free accessibility for all users.

---

## ⚙️ Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/VarnikaMishra/Bharat-Guardian-AI.git](https://github.com/VarnikaMishra/Bharat-Guardian-AI.git)
    cd Bharat-Guardian-AI
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install requirements:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure API Keys:**
    Create a `.env` file in the root directory:
    ```text
    GOOGLE_API_KEY=your_gemini_api_key_here
    ```

5.  **Launch the Application:**
    ```bash
    streamlit run submit.py
    ```

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

---
**Developed by Varnika Mishra** *Harnessing AI to protect and empower.*
