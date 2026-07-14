import streamlit as st
import pandas as pd
import random

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="SDOH Risk Predictor", layout="wide")


# --- 1. DATA GENERATION & LOGIC ENGINE ---
def load_mock_data():
    """Generates 50 mock patients."""
    data = []
    languages = ['English', 'Spanish', 'Mandarin', 'Vietnamese']

    for i in range(1, 51):
        data.append({
            "Patient ID": f"PT-{1000 + i}",
            "Age": random.randint(35, 85),
            "Distance to Pharmacy (mi)": round(random.uniform(0.5, 15.0), 2),
            "Has Vehicle": random.choice(['Yes', 'No', 'No', 'Yes']),
            "Primary Language": random.choice(languages),
            "Number of Meds": random.randint(1, 8)
        })
    return pd.DataFrame(data)


def apply_clinical_logic(df):
    """Calculates SDOH Risk Score dynamically, safely handling empty cells if a user adds a blank row."""
    df = df.copy()  # Prevent altering the original data unexpectedly
    scores = []
    levels = []

    for _, row in df.iterrows():
        score = 0

        # Safely get values, defaulting to 0 or 'English' if a nurse left a cell blank
        distance = row.get('Distance to Pharmacy (mi)', 0)
        if pd.isna(distance): distance = 0

        vehicle = str(row.get('Has Vehicle', 'Yes')).strip().title()
        language = str(row.get('Primary Language', 'English')).strip().title()

        # Weighted Scoring Logic
        if distance > 5: score += 3
        if vehicle == 'No': score += 5
        if language != 'English': score += 2

        # Categorize Risk
        scores.append(score)
        if score >= 7:
            levels.append("High")
        elif score >= 4:
            levels.append("Medium")
        else:
            levels.append("Low")

    df['Risk Score'] = scores
    df['Risk Level'] = levels
    return df


# --- 2. APPLICATION MEMORY (SESSION STATE) ---
if 'patient_data' not in st.session_state:
    raw_df = load_mock_data()
    st.session_state.patient_data = apply_clinical_logic(raw_df)

if 'uploaded_filename' not in st.session_state:
    st.session_state.uploaded_filename = None

# --- 3. SIDEBAR NAVIGATION & UPLOAD ---
st.sidebar.title("Care Dashboard")
st.sidebar.markdown("Discharge Planning & Medication Adherence")
st.sidebar.divider()

st.sidebar.write("**Data Source**")
uploaded_file = st.sidebar.file_uploader("Upload Patient Data (CSV)", type=["csv"])

if uploaded_file is not None and uploaded_file.name != st.session_state.uploaded_filename:
    raw_df = pd.read_csv(uploaded_file)
    st.session_state.patient_data = apply_clinical_logic(raw_df)
    st.session_state.uploaded_filename = uploaded_file.name
    st.rerun()

if st.sidebar.button("Randomize Patient Data"):
    raw_df = load_mock_data()
    st.session_state.patient_data = apply_clinical_logic(raw_df)
    st.session_state.uploaded_filename = None
    st.rerun()

st.sidebar.divider()

current_df = st.session_state.patient_data
high_risk_count = len(current_df[current_df['Risk Level'] == 'High'])
st.sidebar.metric(label="Total Discharges", value=len(current_df))
st.sidebar.metric(label="High Risk Patients", value=high_risk_count)

st.sidebar.divider()

st.sidebar.write("**Select a Patient**")
patient_list = ["View All Patients"] + list(current_df['Patient ID'].astype(str))
selected_patient = st.sidebar.selectbox("Navigation", patient_list)

# --- 4. MAIN DASHBOARD (VIEW & EDIT ALL) ---
if selected_patient == "View All Patients":
    st.title("Medication Adherence Risk Predictor")
    st.write(
        "This dashboard analyzes Social Determinants of Health (SDOH) to predict medication non-adherence. **Double-click any cell to edit data. Scroll to the bottom to add a new patient row.** Risk scores will update automatically.")

    # --- TRANSPARENCY / LOGIC EXPLANATION ---
    with st.expander("Clinical Logic: How Risk Scores are Calculated"):
        st.markdown("""
        **Risk Factors & Point Values:**
        * **Distance to Pharmacy > 5 miles:** +3 points
        * **Has No Vehicle:** +5 points
        * **Primary Language Not English:** +2 points

        **Risk Thresholds:**
        * **High Risk (Red):** 7 or more points
        * **Medium Risk (Yellow):** 4 to 6 points
        * **Low Risk (Green):** 0 to 3 points

        *Note: These weights are based on clinical guidelines for Social Determinants of Health (SDOH) barriers to medication adherence.*
        """)


    # --- COLOR CODING LOGIC ---
    def color_risk(val):
        """Applies background and text color based on risk level."""
        if val == 'High':
            return 'background-color: #ffcccc; color: #900000;'  # Light Red background, Dark Red text
        elif val == 'Medium':
            return 'background-color: #ffe4b5; color: #8a6300;'  # Light Yellow background, Dark Yellow text
        elif val == 'Low':
            return 'background-color: #ccffcc; color: #005000;'  # Light Green background, Dark Green text
        return ''


    # Apply the color style to our current dataframe
    styled_df = current_df.style.map(color_risk, subset=['Risk Level'])

    # Render the interactive data editor with the styled dataframe
    edited_df = st.data_editor(
        styled_df,
        num_rows="dynamic",
        disabled=["Risk Score", "Risk Level"],
        use_container_width=True,  # Keeping this standard formatting
        column_config={
            "Distance to Pharmacy (mi)": st.column_config.NumberColumn(format="%.2f"),
            "Risk Level": st.column_config.TextColumn(help="Auto-calculated based on SDOH factors")
        }
    )

    # Re-calculate if the user makes edits to the table
    if not edited_df.equals(current_df):
        st.session_state.patient_data = apply_clinical_logic(edited_df)
        st.rerun()

    st.divider()

    # --- DOWNLOAD BUTTON ---
    st.subheader("Export Data")
    st.write("Download the current patient roster (including risk scores and your recent edits) to your computer.")

    csv_data = st.session_state.patient_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Patient Data as CSV",
        data=csv_data,
        file_name="Updated_Patient_Risk_Data.csv",
        mime="text/csv",
    )

# --- 5. INDIVIDUAL PATIENT VIEW ---
else:
    patient_row = current_df[current_df['Patient ID'].astype(str) == selected_patient]

    if not patient_row.empty:
        patient_data = patient_row.iloc[0]
        risk = patient_data['Risk Level']

        st.title(f"Patient Profile: {selected_patient}")

        if risk == 'High':
            st.error(f"RISK LEVEL: {risk} (Score: {patient_data['Risk Score']})")
        elif risk == 'Medium':
            st.warning(f"RISK LEVEL: {risk} (Score: {patient_data['Risk Score']})")
        else:
            st.success(f"RISK LEVEL: {risk} (Score: {patient_data['Risk Score']})")

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Clinical Data")
            st.write(f"**Age:** {patient_data.get('Age', 'N/A')}")
            st.write(f"**Number of Prescriptions:** {patient_data.get('Number of Meds', 'N/A')}")
        with col2:
            st.subheader("SDOH Data")
            formatted_distance = "{:.2f}".format(float(patient_data.get('Distance to Pharmacy (mi)', 0)))
            st.write(f"**Distance to Pharmacy:** {formatted_distance} miles")
            st.write(f"**Has Vehicle:** {patient_data.get('Has Vehicle', 'N/A')}")
            st.write(f"**Primary Language:** {patient_data.get('Primary Language', 'N/A')}")

        st.divider()

        st.subheader("Suggested Interventions")

        if risk in ['High', 'Medium']:
            distance = float(patient_data.get('Distance to Pharmacy (mi)', 0))
            vehicle = str(patient_data.get('Has Vehicle', 'Yes')).strip().title()
            language = str(patient_data.get('Primary Language', 'English')).strip().title()

            if distance > 5 and vehicle == 'No':
                st.info("Logistics Barrier: Patient lacks transportation and lives far from a pharmacy.")
                if st.button("Arrange Mail-Order Pharmacy Delivery"):
                    st.success("Success! Mail-order pharmacy request sent to discharge team.")
                if st.button("Schedule Uber Health Ride to Pharmacy"):
                    st.success("Success! Uber Health ride scheduled for patient's discharge day.")

            if language != 'English':
                st.info(f"Health Literacy Barrier: Patient primarily speaks {language}.")
                if st.button(f"Print Med Instructions in {language}"):
                    st.success("Success! Translated instructions sent to the nursing station printer.")
        else:
            st.write("Patient is low risk. Standard discharge protocol applies.")
    else:
        st.error("Patient not found. They may have been deleted from the database.")