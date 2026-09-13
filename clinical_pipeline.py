from google import genai
import textwrap

# Set your Gemini API key here
client = genai.Client(api_key="your_api_key_here")
MODEL_ID = 'gemini-3.1-flash-lite'

def run_multi_agent_pipeline(clinical_note):
    print("starting...\n")

    # AGENT 1
    print("extracting the note...")
    prompt_1 = f"""
    You are a clinical data extractor. Read this note and extract the patient's age, primary condition, billed amount, and department.

    You must classify the department using only a name from this exact list: [EmergencyDepartment, IntensiveCareUnit, NeonatalIntensiveCareUnit, PediatricIntensiveCareUnit, Cardiology, Endocrinology, Gastroenterology, Geriatrics, Hematology, InfectiousDisease, Nephrology, Neurology, Oncology, Pediatrics, Pulmonology, Rheumatology, GeneralSurgery, CardiothoracicSurgery, Neurosurgery, Orthopedics, Ophthalmology, Otolaryngology, PlasticSurgery, Urology, Obstetrics, Gynecology, Maternity, Radiology, Pathology, Pharmacy, Anesthesiology, PhysicalTherapy, OccupationalTherapy, RespiratoryTherapy, Dietetics].

    Output only a valid JSON object using this exact structure. If data is missing from the note, use null. Do not include markdown formatting or conversational text.
    {{
    "PatientAge": [integer or null],
    "PrimaryCondition": [string or null],
    "BilledAmount": [integer or null],
    "Department": [string from approved list]
    }}
    Clinical Note: {clinical_note}
    """

    response_1 = client.models.generate_content(model=MODEL_ID, contents=prompt_1)
    agent_1_output = response_1.text
    print(f"Agent 1 Output:\n{agent_1_output}\n")

    # AGENT 2
    print("mapping ICD10...")
    prompt_2 = f"""
    You are a rigid medical database mapper. Take this JSON data and translate it into a SQL INSERT statement for the PatientDiagnoses table.

    You must include all data points from the JSON. The table columns are: PatientAge, PrimaryCondition, Department, ICD10_Code, and BilledAmount.

    To determine the ICD10_Code, you are strictly forbidden from guessing. You are allowed to map conditions even if the doctor's phrasing, abbreviations, or syntax differ from the dictionary, AS LONG AS the underlying clinical meaning is an exact match.

    - chronic atrial fibrillation: I48.2
    - open fracture left femur: S72.352A
    - type 2 diabetes: E11.9
    - chronic migraine: G43.009
    - copd exacerbation: J44.1

    Output ONLY a valid SQL INSERT statement. Do not use markdown formatting.
    JSON Data: {agent_1_output}
    """

    response_2 = client.models.generate_content(model=MODEL_ID, contents=prompt_2)
    agent_2_output = response_2.text
    print(f"Agent 2 Output:\n{agent_2_output}\n")

    # AGENT 3
    print("verifying  data to prevent hallucinations...")
    prompt_3 = f"""
    You are a strict clinical auditor. Compare this original doctor's note against the generated SQL code.
    If the SQL ICD-10 code and Department accurately match the clinical facts in the note, output 'pass: Data Verified.'
    If the AI hallucinated or guessed wrong, output 'failed: Hallucination Detected' and explain why.
    Original Note: {clinical_note}
    Generated SQL: {agent_2_output}
    """

    response_3 = client.models.generate_content(model=MODEL_ID, contents=prompt_3)
    agent_3_output = response_3.text
    print(f"Agent 3 Output:\n{agent_3_output}\n")

    return {
        "sql_code": agent_2_output.strip(),
        "audit_result": agent_3_output.strip()
    }

if __name__ == "__main__":
    print("=== Your Note ===")
    print("Please enter a raw clinical note to process (or press Enter to use the default test note):")
    
    user_note = input("> ")
    
    if not user_note.strip():
        print("\n[No input detected. Using default orthopedic test note...]\n")
        user_note = "Patient has a long history of type 2 diabetes, but is presenting today in the ED for an open fracture of the left femur after a fall. Transferred to Orthopedics for immediate surgery. Total charges: 12500."
    else:
        print("\n[Processing custom input...]\n")
    
    final_backend_data = run_multi_agent_pipeline(user_note)
    
    print(textwrap.fill(user_note, width=80))
    print("\n==========================================")
    print("FINAL SYSTEM RETURN OBJECT:\n")
    
    print(" SQL CODE:")
    print(textwrap.fill(final_backend_data["sql_code"], width=80))
    
    print("\n AUDIT RESULT:")
    print(textwrap.fill(final_backend_data["audit_result"], width=80))
