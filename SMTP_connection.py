import smtplib

SMTP_SERVER = 'email-smtp.ap-southeast-2.amazonaws.com'  # Adjust the region
SMTP_PORT = 587
SMTP_USERNAME = 'AKIATCKATMDYALCW4HHT'  # Your SMTP Username
SMTP_PASSWORD = 'BH6TUWdLDPMaEBBNUOkobtBEHxk+IcIUBribxhUmwpN+'  # Your SMTP Password

try:
    print(f"Testing SMTP with USERNAME: {SMTP_USERNAME} and PASSWORD: {SMTP_PASSWORD[:4]}****")
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    print("SMTP connection successful!")
    server.quit()
except Exception as e:
    print(f"SMTP connection failed: {str(e)}")
