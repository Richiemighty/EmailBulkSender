import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO

# --- Configuration ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_NAME = "Victoria Kehinde"
SENDER_EMAIL = "richiemighty5@gmail.com"
SENDER_PASSWORD = st.secrets["email_password"]
LOGO_URL = "https://fadacresources.com/Fadac%20Logo%202000x1000.png"

# --- HTML Template ---
def generate_html_email(name):
    return f"""
    <div style="background-color: white; padding: 30px; border-radius: 8px; max-width: 700px; margin: auto; box-shadow: 0 2px 10px rgba(0,0,0,0.1); font-family: Arial, sans-serif; color: #333;">
        <p>Dear {name},</p>
        <p>Trust this mail meets you well,</p>
        <p>My name is Victoria, I am a Recruitment Associate for Fadac Resources.</p>
        <p>Fadac Resources is a Recruitment and Outsourcing Firm, we help companies in terms of recruitment, payroll management, and management of staff. We have recruited several roles for various companies all over Africa and North-America.</p>
        <p>We, as an HR consulting firm, will help find competent professionals who will fit into vacant positions in your organization. We would like to assist your HR department in its talent acquisition and management strategy.</p>
        <p>Are you available for a brief call anytime? Please let me know when it would be convenient to meet with our team.</p>
        <p>Kind regards,</p><br>
        <p><strong>Victoria Kehinde</strong><br>{SENDER_EMAIL}<br>Support Executive | Fadac Resources</p>
        <p><img src="{LOGO_URL}" width="180"></p>
        <p><strong>Nigeria:</strong> 19 Adebare Street, Ogudu, Lagos<br>
           <strong>Canada:</strong> 5 Tombrown Drive. Paris. Brant. N3L 0N5</p>
        <hr>
        <small style="font-size: 11px;">
            Confidentiality: This communication is only for the use of the addressee...<br><br>
            Security Warning: This e-mail is not a 100% secure communications medium...<br><br>
            Viruses: Please ensure the recipient verifies that the email is virus-free...
        </small>
    </div>
    """

# --- Email Sender ---
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
        return f"❌ Failed to send to {to_email}: {e}"

# --- Streamlit UI ---
st.set_page_config("📨 Email Preview & Sender", layout="wide")
st.title("📬 Bulk Email Sender with Preview and Status Tracker")

uploaded_file = st.file_uploader("📤 Upload CSV (Name, Email, Status)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if not all(col in df.columns for col in ['Name', 'Email', 'Status']):
        st.error("CSV must include: Name, Email, Status")
    else:
        df['Status'] = df['Status'].fillna("").astype(str).str.strip().str.upper()
        df_to_send = df[df['Status'] != "SENT"].copy()

        if df_to_send.empty:
            st.success("🎉 All emails have already been sent.")
        else:
            st.success(f"📋 {len(df_to_send)} unsent recipients found.")

            # Initialize preview index
            if 'preview_index' not in st.session_state:
                st.session_state.preview_index = 0
            def next_preview(): st.session_state.preview_index = (st.session_state.preview_index + 1) % len(df_to_send)
            def prev_preview(): st.session_state.preview_index = (st.session_state.preview_index - 1) % len(df_to_send)

            # Navigation controls
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1: st.button("⬅️ Previous", on_click=prev_preview)
            with col2: st.markdown(f"<center>**Previewing {st.session_state.preview_index + 1} of {len(df_to_send)}**</center>", unsafe_allow_html=True)
            with col3: st.button("➡️ Next", on_click=next_preview)

            # Display current preview
            current_row = df_to_send.iloc[st.session_state.preview_index]
            st.markdown(f"### ✉️ Preview: {current_row['Name']} - {current_row['Email']}")
            st.components.v1.html(generate_html_email(current_row['Name']), height=600, scrolling=True)

            colA, colB = st.columns(2)

            # Status log tracker
            status_log = []

            with colA:
                if st.button("📧 Send to This Recipient"):
                    result = send_html_email(current_row['Email'], current_row['Name'])
                    if result is True:
                        st.success(f"✅ Email sent to {current_row['Name']}")
                        df.loc[df['Email'] == current_row['Email'], 'Status'] = 'SENT'
                    else:
                        st.error(result)

            with colB:
                if st.button("🚀 Send to All Unsent Recipients"):
                    success = 0
                    log_msgs = []
                    with st.spinner("Sending emails..."):
                        for _, row in df_to_send.iterrows():
                            result = send_html_email(row['Email'], row['Name'])
                            if result is True:
                                success += 1
                                df.loc[df['Email'] == row['Email'], 'Status'] = 'SENT'
                                log_msgs.append(f"✅ Sent: {row['Email']}")
                            else:
                                log_msgs.append(result)

                    st.success(f"✅ Sent {success} emails successfully.")
                    st.info("📄 Status Log:")
                    for msg in log_msgs:
                        st.markdown(f"- {msg}")

            # Allow download of updated file
            st.markdown("---")
            st.markdown("### 📥 Download Updated CSV (with SENT status)")
            updated_csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📁 Download CSV",
                data=updated_csv,
                file_name="updated_emails.csv",
                mime="text/csv"
            )
