# 🩺 Rehcura – AI Clinical Note Triage & Analytics Prototype

## 💡 Inspiration

I was inspired by the immense administrative burden faced by healthcare professionals today. While EHRs like Epic and Cerner are powerful, they often lead to information overload. I saw an opportunity to use AI and NLP to automate the critical, yet tedious, task of triaging clinical notes, helping clinicians save time and prioritize urgent patient care.

## ✨ What it does

**Rehcura** is a hackathon prototype that analyzes and triages clinical notes using AI. It can:

-   **Triage Notes:** Automatically classifies notes by urgency (Low, Medium, High) and medical topic.
-   **Generate Summaries:** Creates AI-generated audio and text summaries for quick, hands-free review.
-   **Visualize Data:** Produces word clouds and an interactive analytics dashboard for quick insights from patient data in a CSV file.

## ⚙️ How I built it

I built the project using **Python**, creating a pipeline that integrates several libraries. I used **Natural Language Processing (NLP)** to analyze the note text. For the user interface, I chose **Gradio** because it allowed me to quickly build an interactive, shareable web app. I used **pandas** to handle data and **Plotly** and **WordCloud** for visualization. The audio features were built using **SpeechRecognition** for input and **gTTS** for output.

## 🏃‍♀️ Challenges I ran into

The main challenge was the lack of a large, pre-labeled dataset for clinical notes. I had to combine a small labeled dataset with a rule-based system to make the AI model functional for the prototype. Another challenge was managing the project scope within a limited timeframe, which meant focusing on a core, demonstrable set of features rather than attempting full-scale EHR integration.

## 🎉 Accomplishments I'm proud of

I am most proud of creating a working prototype that successfully demonstrates a clear, real-world application of AI in healthcare. It's a comprehensive solution, not just a single feature. I'm also proud that I was able to build the entire project on my own, from the backend logic to the front-end interface, all within the hackathon's time limit.

## 🧠 What I learned

I learned a tremendous amount about the nuances of applying AI to a specialized field like medicine. I discovered that a simple, elegant UI is crucial for user adoption, especially in high-stress environments. Most importantly, I learned the value of effective scoping and rapid prototyping to turn a complex idea into a functional demo.

## 🚀 What's next for Rehcura

The next steps for Rehcura would be to move beyond the prototype phase. This includes:

-   **Secure Integration:** Developing secure, API-based integration with real EHR systems like **Epic** and **Cerner**.
-   **Advanced Analytics:** Building more robust analytics and predictive models for a deeper understanding of patient trends.
-   **Clinical Validation:** Collaborating with healthcare professionals to validate the urgency scoring and other AI outputs to ensure they are medically sound and reliable.

## 🛠️ Built With

* **Languages:** Python
* **Frameworks:** Gradio
* **APIs:** Google Translate API (via the gTTS library)
* **Libraries:** `pandas`, `scikit-learn`, `Plotly`, `WordCloud`, `SpeechRecognition`, `gTTS`, `spaCy`
* **Concepts:** Natural Language Processing (NLP), Machine Learning, Data Visualization

## 💻 Getting Started

### Prerequisites
* Python 3.x
* `pip` package manager

### Installation
1.  Clone the repository:
    ```bash
    git clone [https://github.com/your-username/Rehcura-Hackathon.git](https://github.com/your-username/Rehcura-Hackathon.git)
    cd Rehcura-Hackathon
    ```
2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the application:
    ```bash
    python app.py
    ```
    The application will launch in your browser at a local address (e.g., http://127.0.0.1:7860).

---

### **Disclaimer**

This is a proof-of-concept prototype built for a hackathon. It is not intended for actual clinical use. The urgency scores and AI outputs are estimates and have not been medically validated.

---
