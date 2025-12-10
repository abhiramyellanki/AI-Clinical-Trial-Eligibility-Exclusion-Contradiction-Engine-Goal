# AI-Clinical-Trial-Eligibility-Exclusion-Contradiction-Engine-Goal# 🔬 Clinical Trial Eligibility Engine

This project is a **Full-Stack MLOps Application** designed to automate the process of determining a patient's eligibility for a clinical trial. It uses an AI model (Gemini) to perform complex text-based comparisons between a patient's profile and a trial's official protocol document.

The application is split into two main services: a React frontend and a FastAPI backend.

## ✨ Features

* **PDF/Text Protocol Analysis:** Accepts official trial protocols in PDF format and extracts criteria.
* **Gemini-Powered Logic:** Uses the Gemini LLM to compare patient data against Inclusion/Exclusion criteria.
* **Detailed Reporting:** Generates a structured report detailing every met and violated criterion, including "Silent Exclusion Triggers."
* **Fully Deployed:** Continuous Integration/Deployment (CI/CD) pipelines ensure the application is always live.

## 🚀 Live Application Status

| Service | Platform | Status | URL |
| :--- | :--- | :--- | :--- |
| **Frontend (UI)** | Vercel | **Live** | `[INSERT YOUR LIVE VERCELL URL HERE]` |
| **Backend (API)** | Render | **Live** | `[INSERT YOUR LIVE RENDER URL HERE]` |

---

## 🏗️ Architecture

The project follows a standard decoupled architecture:

1.  **Frontend:** Built with **React** and **Vite**, responsible for the user interface, form handling, and file uploads.
2.  **Backend:** Built with **FastAPI** (Python), responsible for API routing, file processing, and making the secure call to the LLM.
3.  **LLM:** **Google Gemini API** is used for the core eligibility logic (a form of **Retrieval-Augmented Generation - RAG**).



## 💻 Local Setup (for Developers)

To run the entire project locally, follow the instructions in the respective subdirectories.

### 1. Backend Setup

See the instructions in the **`backend/README.md`** file.

### 2. Frontend Setup

See the instructions in the **`frontend/README.md`** file.

---

## 👤 Contact

| Name | Role | Email |
| :--- | :--- | :--- |
| **Abhiram Yellanki** | Lead Developer | `yellankiabhiram@gmail.com` |