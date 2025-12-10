import os
import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleEDA
from pydantic import BaseModel

# Correct imports for the modern Google GenAI SDK
from google import generativeai
from google.generativeai.errors import APIError

# Library for reading PDF content
try:
    from pypdf import PdfReader
except ImportError:
    # If pypdf fails, try the older library as a fallback (though pypdf is preferred)
    from PyPDF2 import PdfReader 

# --- CONFIGURATION ---
# The model name for complex reasoning tasks
GEMINI_MODEL = "gemini-2.5-pro" # Recommended for detailed analysis of clinical protocols

# Initialize FastAPI app
app = FastAPI(
    title="AI Clinical Trial Eligibility Engine",
    description="Analyzes patient data against a trial protocol using the Gemini API."
)

# Configure CORS (Crucial for the React frontend to communicate with this backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Be more restrictive in production (e.g., ["http://localhost:3000"])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Gemini Client
try:
    # The client automatically picks up the GEMINI_API_KEY environment variable.
    # We explicitly check for it to provide a clearer error message.
    if not os.getenv("GEMINI_API_KEY"):
        raise EnvironmentError("GEMINI_API_KEY environment variable is not set.")
        
    client = generativeai.Client()
    print("Gemini Client successfully initialized.")

except (EnvironmentError, Exception) as e:
    # This RuntimeError is what the user was getting, so we wrap the error correctly
    # to stop the application startup if the API key is missing.
    # In a production environment, FastAPI prefers this to occur during startup.
    # For a simple Render setup, raising the exception on import will halt the server.
    print(f"Error configuring Gemini API: {e}")
    # Instead of an immediate raise, we can use a dependency or check it on the route, 
    # but for simplicity, we'll keep the client initialized (or None) and check it later.
    client = None
    # We will raise an HTTP 503 error if the client is None in the endpoint.


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
                text_content += page.extract_text() or ""
                
            if not text_content.strip():
                raise ValueError("Could not extract any meaningful text from the PDF.")
                
            return text_content
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to read PDF file: {e}"
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
    if client is None:
         raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not configured. Check if GEMINI_API_KEY is set correctly."
        )
        
    try:
        # 1. Extract text from the uploaded protocol file
        protocol_text = extract_text_from_file(protocol_file)
        
        # 2. Construct the detailed prompt for the LLM
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
        2. **Inclusion Criteria Check:** List all inclusion criteria and state whether the patient meets each one (Mets/Not Met).
        3. **Exclusion Criteria Check:** List all exclusion criteria and state whether the patient violates each one (Violates/Does Not Violate).
        4. **Summary Table:** Provide a concise table summarizing the final decision, highlighting any criteria that were **Not Met** (Inclusion) or **Violated** (Exclusion).
        """

        # 3. Call the Gemini API
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=generativeai.types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        
        # 4. Return the result in the format expected by the React frontend
        return JSONResponse(
            content={"result_markdown": response.text},
            status_code=status.HTTP_200_OK
        )

    except APIError as e:
        # Handle specific Gemini API errors (e.g., invalid key, rate limiting)
        print(f"Gemini API Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI processing failed due to an API error: {e}"
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