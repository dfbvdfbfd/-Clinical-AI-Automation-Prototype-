# -Clinical-AI-Automation-Prototype

Business Problem: Manual clinical coding causes delays and systemic data corruption.
Solution: Multi-agent pipeline that translates clinical notes to SQL by extracting patient data and mapping conditions to ICD-10, with an "Auditor" agent to detect hallucinations. 

the pipeline maps does not load the full ICD-10 registry to prevent exceeding api token limits --> uses a restricted dictionary instead


