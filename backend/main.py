import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai  # Correct import for the 'google-genai' package # Corrected Import
from dotenv import load_dotenv
from pypdf import PdfReader
from io import BytesIO
# Removed duplicate FastAPI and CORSMiddleware imports

# Load environment variables from .env file
load_dotenv()

# --- 1. LLM CLIENT SETUP (CORRECTED) ---
# Fetch the key from environment variables (Render uses this)
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_KEY:
    # This will prevent the app from starting if the key is missing on Render
    raise RuntimeError("GEMINI_API_KEY environment variable not found. Please ensure it is set on Render.")

# Configure the API key globally using genai.configure(). 
# This is the correct method for the SDK version you are using.
try:
    genai.configure(api_key=GEMINI_KEY)
except Exception as e:
    # The app will exit here if the key is invalid or configuration fails
    raise RuntimeError(f"Error configuring Gemini API: {e}")

# The 'client' object is no longer needed; we use 'genai.models' directly.
# --- END LLM CLIENT SETUP ---


# --- 2. FASTAPI APP SETUP ---
app = FastAPI(title="Clinical Trial Eligibility Engine MVP (PDF Ready)")

# --- CORS Configuration ---
# Combined and cleaned up CORS configuration.

# You MUST replace the placeholder with your *actual* Vercel URLs
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "AI Eligibility Engine API"}

client = genai.Client()
# --- CORE ENDPOINT ---
@app.post("/analyze_eligibility/")
async def analyze_eligibility(
    patient_data: str = Form(...),
    protocol_file: UploadFile = File(...),
):
    """
    Analyzes patient data against a trial protocol, supporting PDF file uploads.
    """
    
    # 3. READ & EXTRACT PROTOCOL CONTENT (PDF Extraction Logic)
    protocol_content = ""
    try:
        # Check if the file is a PDF (optional, but good practice)
        if not protocol_file.filename.lower().endswith('.pdf'):
            # Fallback for TXT files (if user uploads .txt instead of .pdf)
            if protocol_file.filename.lower().endswith('.txt'):
                protocol_content = (await protocol_file.read()).decode("utf-8")
            else:
                raise ValueError("Unsupported file type. Please upload a .pdf or .txt file.")
        
        else: # Handle .pdf file
            # Read the file content into memory as bytes
            pdf_bytes = await protocol_file.read()
            
            # Use PdfReader to open the byte stream
            pdf_reader = PdfReader(BytesIO(pdf_bytes))
            
            # Loop through all pages and extract text
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    protocol_content += text + "\n\n"
        
        if not protocol_content.strip():
            raise ValueError("Could not extract any meaningful text from the file.")
            
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Handle general file or parsing errors
        raise HTTPException(status_code=500, detail=f"Error processing file: {e}")
    
    # 4. THE PROMPT ENGINEERING (Contradiction Logic - unchanged)
    prompt = f"""
    You are a highly accurate **Clinical Trial Eligibility and Contradiction Engine**. Your task is to compare the provided Patient Profile against the Clinical Trial Protocol and generate a final eligibility decision, a reasoning breakdown, and specifically identify any "silent exclusion triggers."

    **INSTRUCTIONS:**
    1.  **Analyze** the **Patient Profile** against the **Trial Protocol**.
    2.  Determine the **Final Decision**: 'Eligible' or 'Ineligible'.
    3.  Generate a summary of **Inclusion Matches** and **Exclusion Rejections**.
    4.  **CRITICALLY**: Look for subtle contradictions where a patient meets a broad inclusion criterion but violates a highly specific exclusion criterion. This is the **Hidden Contradiction** section.
    5.  The entire output MUST be formatted strictly using **Markdown**.

    ---
    ## 🧬 Patient Profile
    {patient_data}

    ---
    ## 📑 Trial Protocol Text
    {protocol_content}

    ---
    ## 🔬 ANALYSIS REPORT
    
    **Final Decision:** [Eligible or Ineligible]
    
    ### 🟢 Inclusion Criteria Met
    * [List the specific criteria the patient meets.]
    
    ### 🔴 Exclusion Criteria Violated
    * [List the specific criteria the patient fails, or state "None".]
    
    ### 🚨 Hidden Contradiction (Silent Exclusion Trigger)
    [Explain the core contradiction, focusing on the patient's data violating an exclusion even if it met an inclusion. Clearly state the reason for ineligibility.]
    """

    # 5. CALL GEMINI API (UPDATED SYNTAX)
    try:
        # We call genai.models directly because genai.configure() was used
        response = client.generate_content( 
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        # 6. RETURN THE MARKDOWN OUTPUT
        return {"result_markdown": response.text}
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        # Return a 500 status if the LLM processing itself fails
        raise HTTPException(status_code=500, detail="LLM processing failed. Check API key and quota.")