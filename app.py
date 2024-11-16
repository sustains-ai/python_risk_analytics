from flask import Flask
from create_app import create_app  # Import the create_app function

# Create the app using the create_app function
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
