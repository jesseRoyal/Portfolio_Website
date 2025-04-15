import smtplib

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL = 'educationsports7@gmail.com'  # Your Gmail
PASSWORD = 'jturzqljlaraggdc'   # App Password (or Gmail password if "Less Secure Apps" is on)

try:
    print("⌛ Connecting to SMTP server...")
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()  # Enable encryption
    print("🔐 Logging in...")
    server.login(EMAIL, PASSWORD)
    print("✅ SMTP connection successful!")

    # Optional: Send a test email
    print("📤 Sending test email...")
    server.sendmail(
        from_addr=EMAIL,
        to_addrs=EMAIL,  # Send to yourself
        msg="Subject: SMTP Test\n\nThis is a manual SMTP test."
    )
    print("📩 Test email sent!")

except Exception as e:
    print(f"❌ SMTP Error: {e}")
finally:
    server.quit()  # Close connection