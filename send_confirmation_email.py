def send_confirmation_email(user_email):
    token = s.dumps(user_email, salt='email-confirm')
    msg = Message('Confirm Your Email', recipients=[user_email])
    link = url_for('main.confirm_email', token=token, _external=True)
    msg.body = f'Please confirm your email address by clicking on the following link: {link}'

    try:
        mail.send(msg)
        current_app.logger.info(f"Confirmation email sent to {user_email}")
    except Exception as e:
        current_app.logger.error(f"Failed to send confirmation email: {str(e)}")
