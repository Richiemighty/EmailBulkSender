import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# --- Configuration ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_NAME = "Victoria Kehinde"
SENDER_EMAIL = "richiemighty5@gmail.com"
SENDER_PASSWORD = st.secrets["email_password"]
LOGO_URL = "https://fadacresources.com/Fadac%20Logo%202000x1000.png"

# --- HTML Email Template ---
def generate_html_email(name):
    return f"""
    <p>Dear {name},</p>
    <p>Trust this mail meets you well,</p>
    <p>My name is Victoria, I am a Recruitment Associate for Fadac Resources.</p>
    <p>Fadac Resources is a Recruitment and Outsourcing Firm, we help companies in terms of recruitment, payroll management, and management of staff. We have recruited several roles for various companies all over Africa and North-America.</p>
    <p>We, as an HR consulting firm, will help find competent professionals who will fit into vacant positions in your organization. We would like to assist your HR department in its talent acquisition and management strategy.</p>
    <p>Are you available for a brief call anytime? Please let me know when it would be convenient to meet with our team.</p>
    <p>Kind regards,</p><br><br>
    <p><strong>Victoria Kehinde</strong> | {SENDER_EMAIL} | Support Executive | Fadac Resources</p>
    <p><img src="{LOGO_URL}" alt="Fadac Resources Logo" width="200"></p>
    <p><strong>Nigeria:</strong> 19 Adebare Street, Ogudu, Lagos<br>
    <strong>Canada:</strong> 5 Tombrown Drive. Paris. Brant. N3L 0N5</p>
    <hr>
    <small>
        Confidentiality: This communication is only for the use of the addressee. It may contain information which is legally privileged, confidential and exempt from disclosure. If you are not the intended recipient you must not read, copy, distribute or disseminate this communication or any attachments to anyone other than the addressee or use the information it contains. If you receive this communication in error, please inform us by telephone at once. Tel: +234 908 600 0078 United Kingdom; Email: hello@fadacresources.com website: https://fadacresources.com
        <br><br>
        Security Warning: Please note that this e-mail has been created in the knowledge that Internet e-mail is not a 100% secure communications medium. We advise that you understand and observe this lack of security when e-mailing us. 
        <br><br>
        Viruses: Although we have taken steps to ensure that this e-mail and attachments are free from any virus, we advise that in keeping with good computing practice the recipient should ensure they are actually virus free. Fadac Resources and Services Ltd cannot accept responsibility for any damage or loss caused by this communication media. Fadac Resources and Services Ltd is registered in Nigeria and governed by the laws of the Nigeria.
    </small>
    """

# --- Send HTML Email ---
def send_html_email(to_email, to_name):
    msg = MIMEMultipart('alternative')
    msg['From'] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    msg['To'] = to_email
    msg['Subject'] = "We Match You With Capable Professionals"

    html_content = generate_html_email(to_name)
    msg.attach(MIMEText(html_content, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error sending to {to_email}: {e}")
        return False

# --- Streamlit UI ---
st.set_page_config("Bulk Email Sender", layout="wide")
st.title("📨 HTML Bulk Email Sender")

uploaded_file = st.file_uploader("Upload CSV (columns: Name, Email, Status)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if not all(col in df.columns for col in ['Name', 'Email', 'Status']):
        st.error("CSV must include columns: Name, Email, Status")
    else:
        # 🛠 Fix: Ensure 'Status' is a clean string before filtering
        df['Status'] = df['Status'].fillna("").astype(str).str.strip().str.upper()
        df_to_send = df[df['Status'] != "SENT"]

        st.success(f"{len(df_to_send)} unsent emails found.")

        if not df_to_send.empty:
            st.markdown("### 📬 Email Preview")
            selected = st.slider("Preview recipient", 0, len(df_to_send)-1, 0)
            preview_name = df_to_send.iloc[selected]['Name']
            preview_email = df_to_send.iloc[selected]['Email']

            st.write(f"**Recipient:** {preview_name} - {preview_email}")
            st.components.v1.html(generate_html_email(preview_name), height=400, scrolling=True)

            col1, col2 = st.columns(2)

            with col1:
                if st.button("📧 Send to This Recipient"):
                    if send_html_email(preview_email, preview_name):
                        st.success(f"✅ Email sent to {preview_name} ({preview_email})")

            with col2:
                if st.button("🚀 Send to All Unsent Recipients"):
                    success_count = 0
                    with st.spinner("Sending emails..."):
                        for _, row in df_to_send.iterrows():
                            if send_html_email(row['Email'], row['Name']):
                                success_count += 1
                    st.success(f"✅ Sent {success_count} emails successfully!")
        else:
            st.info("All recipients are already marked as SENT.")
