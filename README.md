SDOH Risk Predictor & Care Dashboard

## The Problem
Every year, millions of patients are discharged from hospitals with life-saving medications, yet up to 50% fail to adhere to their prescriptions. Often, this is due to **Social Determinants of Health (SDOH)** such as transportation barriers or low health literacy. Doctors have access to this data, but it is siloed in complex spreadsheets, making it difficult to use during clinical decision-making.

## Our Solution (Bridging the Gap)
The SDOH Care Dashboard bridges the gap between raw data analytics and clinical medicine. It ingests patient data, runs it through a transparent clinical logic engine, and outputs an interactive, color-coded triage dashboard. 

**Key Features:**
* **Real-time Risk Stratification:** Automatically categorizes patients into High, Medium, or Low risk for medication non-adherence.
* **Interactive UI:** Clinicians can edit patient data on the fly; the logic engine recalculates risk scores instantly.
* **Actionable Interventions:** The dashboard doesn't just display data—it suggests clinical actions (e.g., automated Uber Health rides, Mail-order pharmacy delivery, translated instructions) based on the patient's specific SDOH barriers.
* **Custom CSV Ingestion:** Hospitals can upload their own patient rosters for instant analytics.

## Tech Stack
* **Language:** Python
* **Data Processing:** Pandas
* **Frontend/UI:** Streamlit
