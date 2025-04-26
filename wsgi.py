from portfolio import create_app

# Create the Flask app instance
app = create_app()

# For Vercel, export the app as a WSGI application
application = app