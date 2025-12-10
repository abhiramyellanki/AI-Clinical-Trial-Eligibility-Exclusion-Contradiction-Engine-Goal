# ⚛️ Frontend Service: Clinical Trial Eligibility UI

This directory contains the user interface (UI) for the Eligibility Engine, built with React and Vite.

## 🔗 Dependencies

This project requires a connection to the live FastAPI backend to function.

* **Technology Stack:** React, JavaScript, Vite
* **API Connection:** The application connects to the backend API via the URL defined in `src/EligibilityForm.jsx` (or a similar configuration file).

**Current Live Backend URL:**
`[INSERT YOUR LIVE RENDER API BASE URL HERE, e.g., https://your-backend.onrender.com]`

## ⚙️ Local Development Setup

Follow these steps to run the frontend locally and connect it to a deployed or local backend.

### Prerequisites

You must have **Node.js** and **npm** installed.

### Installation

1.  Navigate into the frontend directory:
    ```bash
    cd frontend
    ```
2.  Install all required Node packages:
    ```bash
    npm install
    ```

### Running Locally

Ensure your backend (either local or deployed) is running and accessible.

1.  Start the development server:
    ```bash
    npm run dev
    ```
2.  The application should open in your browser, typically at **`http://localhost:5173`** (or another port specified by Vite).

### Important Files

* `src/EligibilityForm.jsx`: Contains the main component, state management, and the `fetch` logic for connecting to the backend API.
* `src/App.css` / `tailwind.config.js`: Configuration for styling and layout.