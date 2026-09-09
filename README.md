# SupportPilot

SupportPilot is an intelligent IT support ticketing system built with Flask and Python. It leverages machine learning to automatically classify incoming support tickets, predict their severity, calculate priority based on business impact, and uses a Retrieval-Augmented Generation (RAG) pipeline to suggest resolutions based on an internal knowledge base.

## Features

- **JWT Authentication:** Secure cookie-based JWT authentication using `Flask-JWT-Extended` to protect dashboard and API routes.
- **Submit Tickets:** A user-friendly web interface to submit IT support tickets.
- **AI Classification (Milestone 1):** Uses a trained `scikit-learn` model to automatically categorize tickets into predefined categories (e.g., Network, Hardware, Software).
- **Severity Prediction & Priority:** Automatically assesses the severity of the issue (Critical, High, Medium, Low) using keyword analysis and calculates priority (P1 to P4) based on severity and business impact.
- **RAG Resolution Pipeline (Milestone 2):** Integrates with `google-genai` to automatically retrieve relevant documentation from a local JSON knowledge base and generate suggested resolutions for incoming tickets.
- **Dashboard & Analytics:** A modern UI to view key metrics, deflection rates, open tickets, and category distributions.
- **SQLite Database:** Stores all tickets and their AI-classified metadata in a local SQLite database (`tickets.db`).

## Prerequisites

- Python 3.7 or higher
- API Key for Google Gemini (required for the RAG pipeline)

## Installation

1. **Clone the repository or navigate to the project directory:**
   ```bash
   cd SupportPilot
   ```

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   You must set up your Google API Key for the GenAI RAG engine to work. Set the environment variable:
   - On Windows: `set GEMINI_API_KEY=your_api_key_here`
   - On Mac/Linux: `export GEMINI_API_KEY=your_api_key_here`

## Usage

1. **Train the Machine Learning Model:**
   Before running the application for the first time, you need to train the classification model. This will generate the necessary `.pkl` files in the `models` directory.
   ```bash
   python train_model.py
   ```

2. **Start the Application:**
   Run the Flask development server.
   ```bash
   python app.py
   ```

3. **Access the Web Interface:**
   The application will automatically open in your default web browser at `http://127.0.0.1:5000`. If it doesn't, you can manually navigate to that URL.

4. **Authentication:**
   The application is secured. You will be prompted to sign in. You can use any dummy email and password or the "Sign in with Google" mock button to generate a JWT session cookie and access the dashboard.

## Project Structure

- `app.py`: The main Flask application handling routing, API endpoints, JWT authentication, and database interactions.
- `classifier.py`: Contains the logic for AI classification, severity prediction, and priority calculation (Milestone 1).
- `rag/`: Contains the RAG pipeline (`pipeline.py`), retriever logic, and LLM configuration (Milestone 2).
- `data/`: Contains the `knowledge_base.json` used by the RAG pipeline.
- `database.py`: Handles the SQLite database initialization.
- `train_model.py`: Script to train the `scikit-learn` model and save the vectorizer and classifier.
- `models/`: Directory where the trained `.pkl` models are stored.
- `templates/`: Contains the HTML templates for the web interface.
- `static/`: Static assets like CSS, images, etc.
- `tickets.db`: The SQLite database file (created automatically upon running the app).
- `requirements.txt`: List of Python dependencies including Flask-JWT-Extended and google-genai.

## Technologies Used

- **Flask & Flask-JWT-Extended:** Web framework and secure authentication handling.
- **scikit-learn & joblib:** Machine learning libraries used for text classification.
- **Google GenAI:** Used for the Retrieval-Augmented Generation (RAG) resolution suggestions.
- **SQLite:** Lightweight relational database.
- **Pandas & NumPy:** Data manipulation and analysis.
