import React, { useState } from 'react';
import Markdown from 'react-markdown'; 
import { FaPaperclip, FaFile, FaSpinner, FaCheckCircle, FaExclamationTriangle } from 'react-icons/fa';

const API_URL = 'https://ai-clinical-trial-eligibility-exclusion.onrender.com';

export default function EligibilityForm() {
    const [patientData, setPatientData] = useState('');
    const [protocolFile, setProtocolFile] = useState(null);
    const [result, setResult] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!patientData || !protocolFile) {
            setError("Please provide both patient data and a trial protocol file.");
            return;
        }

        setIsLoading(true);
        setError(null);
        setResult(null);

        const formData = new FormData();
        formData.append('patient_data', patientData);
        formData.append('protocol_file', protocolFile);

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                // Fetch automatically sets 'Content-Type': 'multipart/form-data'
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                // Handle HTTP errors or errors sent from FastAPI (like validation errors)
                throw new Error(data.detail || 'Analysis failed on the server. Check file type and data format.');
            }

            // Success: Set the markdown result from the backend
            setResult(data.result_markdown);

        } catch (err) {
            console.error("API Request Error:", err);
            setError(err.message || 'An unexpected error occurred during API communication.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            // Basic file type check for user feedback
            const acceptedTypes = ['application/pdf', 'text/plain'];
            if (!acceptedTypes.includes(file.type) && !file.name.toLowerCase().endsWith('.txt')) {
                setError("Only PDF and TXT files are supported.");
                setProtocolFile(null);
                return;
            }
        }
        setProtocolFile(file);
        setError(null);
    };

    return (
        <div className="p-8 bg-gray-50 min-h-screen">
            <h1 className="text-3xl font-extrabold text-indigo-800 mb-6 border-b-4 border-indigo-200 pb-3 flex items-center">
                <FaCheckCircle className="mr-3 text-indigo-600"/> AI Clinical Trial Contradiction Engine MVP
            </h1>

            <form onSubmit={handleSubmit} className="flex flex-col md:flex-row gap-6 mb-8 bg-white p-6 rounded-xl shadow-lg">
                
                {/* 1. Patient Profile Input */}
                <div className="flex-1">
                    <label htmlFor="patientData" className="block text-lg font-bold text-gray-800 mb-2">
                        🧬 Patient Profile Data
                    </label>
                    <textarea
                        id="patientData"
                        value={patientData}
                        onChange={(e) => setPatientData(e.target.value)}
                        rows="12"
                        className="w-full border-2 border-gray-300 rounded-lg p-3 shadow-inner focus:ring-indigo-500 focus:border-indigo-500 transition duration-150"
                        placeholder="e.g. Age: 55 years old&#10;Diagnosis: Type 2 Diabetes Mellitus&#10;Current HbA1c: 6.5%&#10;Creatinine Clearance (CrCl): 58 mL/min&#10;History of Malignancy: None"
                    />
                </div>

                {/* 2. Protocol Upload & Button */}
                <div className="flex-1 flex flex-col justify-between">
                    <div>
                        <label htmlFor="protocolFile" className="block text-lg font-bold text-gray-800 mb-2">
                            <FaPaperclip className="inline mr-2"/> Trial Protocol (PDF or TXT)
                        </label>
                        <input
                            type="file"
                            id="protocolFile"
                            onChange={handleFileChange}
                            // Updated accept attribute for PDF/TXT support
                            accept=".pdf, .txt" 
                            className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-100 file:text-indigo-700 hover:file:bg-indigo-200 cursor-pointer transition duration-150"
                        />
                        <p className="mt-2 text-sm text-gray-500">
                            Current File: {protocolFile ? protocolFile.name : 'No file selected'}
                        </p>
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading}
                        className="w-full mt-6 py-3 px-4 border border-transparent rounded-lg shadow-xl text-lg font-bold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-4 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 transition duration-150 flex items-center justify-center"
                    >
                        {isLoading ? (
                            <><FaSpinner className="animate-spin mr-2"/> Analyzing...</>
                        ) : (
                            <><FaFile className="mr-2"/> Analyze Eligibility</>
                        )}
                    </button>
                </div>
            </form>

            {/* --- RESULTS SECTION --- */}
            {error && (
                <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg mb-6 shadow-md flex items-center">
                    <FaExclamationTriangle className="mr-3 text-red-600 text-xl"/> <strong>Error:</strong> {error}
                </div>
            )}
            
            {result && (
                <div className="mt-8 p-6 bg-white border border-gray-200 rounded-xl shadow-2xl">
                    <h2 className="text-2xl font-bold text-indigo-700 mb-4 border-b pb-2">
                        welcome
                    </h2>
                    {/* The 'prose' class from the @tailwindcss/typography plugin formats the Markdown beautifully */}
                    <Markdown className="prose max-w-none text-gray-700">
                        {result}
                    </Markdown>
                </div>
            )}
        </div>
    );
}