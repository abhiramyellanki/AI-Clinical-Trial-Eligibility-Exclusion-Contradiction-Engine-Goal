import os
import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware # Corrected import name
from pydantic import BaseModel

# --- CORRECT IMPORTS FOR THE MODERN 'google-genai' SDK ---
from google.genai import Client
from google.genai.errors import APIError # Correct import path for errors
import google.genai.types as genai_types
#from google import generativeai
# Library for reading PDF content
try:
    from pypdf import PdfReader
except ImportError:
    # Fallback/alternative import if pypdf is not available
    from PyPDF2 import PdfReader 

# --- CONFIGURATION ---
GEMINI_MODEL = "gemini-2.5-pro" # Recommended for detailed analysis of clinical protocols

# Initialize FastAPI app
app = FastAPI(
    title="AI Clinical Trial Eligibility Engine",
    description="Analyzes patient data against a trial protocol using the Gemini API."
)

# Configure CORS (Crucial for the React frontend to communicate with this backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Be more restrictive in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Gemini Client
client = None # Initialize client as None

try:
    # Check for the environment variable, which is the standard way to configure
    if not os.getenv("GEMINI_API_KEY"):
        # We don't raise an EnvironmentError here, but instead let the client 
        # remain None and handle the missing key check inside the endpoint.
        print("Warning: GEMINI_API_KEY environment variable is not set. Service will fail.")
    else:
        # Instantiate the client using the correct class from the new SDK
        client = Client() 
        print("Gemini Client successfully initialized.")

except Exception as e:
    print(f"Error initializing Gemini Client: {e}")
    # Client remains None if initialization fails
    client = None


# --- HELPER FUNCTION ---

def extract_text_from_file(file: UploadFile) -> str:
    """Extracts text content from an uploaded PDF or TXT file."""
    if file.content_type == "text/plain" or file.filename.lower().endswith('.txt'):
        # Read plain text file
        return file.file.read().decode('utf-8')
    
    elif file.content_type == "application/pdf" or file.filename.lower().endswith('.pdf'):
        # Read PDF file
        try:
            # Wrap the file stream in a BytesIO object for PdfReader
            pdf_file = io.BytesIO(file.file.read())
            reader = PdfReader(pdf_file)
            
            text_content = ""
            for page in reader.pages:
                # Use .extract_text() and ensure it's not None
                text_content += page.extract_text() or ""
                
            if not text_content.strip():
                raise ValueError("Could not extract any meaningful text from the PDF.")
                
            return text_content
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to read PDF file. Ensure the PDF is not encrypted or corrupt: {e}"
            )
            
    else:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type. Only PDF and TXT are allowed."
        )


# --- API ENDPOINT ---

@app.post("/analyze_eligibility/")
async def analyze_eligibility(
    patient_data: str = Form(...),
    protocol_file: UploadFile = File(...)
):
    """
    Analyzes patient data against a clinical trial protocol to determine eligibility
    and identify any potential exclusion criteria contradictions.
    """
    # Check 1: Ensure the Gemini Client is available
    if client is None:
         raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not configured. Check if GEMINI_API_KEY is set correctly on the server."
        )
        
    try:
        # 2. Extract text from the uploaded protocol file
        protocol_text = extract_text_from_file(protocol_file)
        
        # 3. Construct the detailed prompt for the LLM
        system_instruction = (
            "You are an expert clinical research associate. Your task is to compare a patient's "
            "profile against the full eligibility (Inclusion/Exclusion) criteria of a clinical trial protocol. "
            "Provide your findings in a clear, highly structured Markdown format."
        )

        prompt = f"""
        # Clinical Trial Eligibility Analysis

        ## Patient Profile:
        {patient_data}

        ---

        ## Trial Protocol Eligibility Criteria:
        {protocol_text}

        ---

        ## Analysis Instructions:
        1. **Final Decision:** State clearly if the patient is **Eligible** or **Not Eligible**.
        2. **Inclusion Criteria Check:** List all inclusion criteria and state whether the patient meets each one (Meets/Not Met).
        3. **Exclusion Criteria Check:** List all exclusion criteria and state whether the patient violates each one (Violates/Does Not Violate).
        4. **Summary Table:** Provide a concise table summarizing the final decision, highlighting any criteria that were **Not Met** (Inclusion) or **Violated** (Exclusion).
        """

        # 4. Call the Gemini API
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=genai_types.GenerateContentConfig( # Ensure 'generativeai.types' is available
                system_instruction=system_instruction
            )
        )
        
        # 5. Return the result in the format expected by the React frontend
        return JSONResponse(
            content={"result_markdown": response.text},
            status_code=status.HTTP_200_OK
        )

    except APIError as e:
        # Handle specific Gemini API errors (e.g., invalid key, rate limiting)
        print(f"Gemini API Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI processing failed due to an API error: The model refused the request or failed. Details: {e}"
        )
    except HTTPException as e:
        # Re-raise explicit HTTP exceptions (like file type or PDF read errors)
        raise e
    except Exception as e:
        # Catch all other unexpected errors
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected server error occurred: {e}"
        )

# --- ROOT PATH FOR HEALTH CHECK ---
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Clinical Trial Eligibility Engine is running."}