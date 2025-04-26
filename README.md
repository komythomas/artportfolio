# Art Portfolio - HSS FineArt (Adapt Name)

    ![License](https://img.shields.io/badge/license-MIT-blue.svg) <!-- Optional: Choose your license -->

## Description

    This project is an art portfolio web application developed with Flask. It allows an artist (Hermann Sebastian Schultz) to showcase their works, manage a gallery, provide information about commissions, and administer the site content via a dedicated interface.

    The site is designed to be deployed on platforms like Vercel or Heroku. You can also deploy it locally on your machine.

## Features

    *   **Home:** Customizable homepage with a background image.
    *   **Gallery:** Displays artworks organized by categories (tags). Shows NFT status, availability, description, and includes an Image Viewer (Lightbox).
    *   **About:** Section to introduce the artist.
    *   **Commissions:** Information about custom artwork orders.
    *   **Contact:** Contact information and links to social media.
    *   **Administration Panel:**
        *   Artwork Management (add, modify, delete) - treated as artist projects.
        *   Tag/Category Management.
        *   Page Management (add, modify, delete).
        *   Image Management (upload for logo, favicon, background image, artworks).
        *   Site Configuration (site name, meta description, etc.).
        *   Google Analytics Integration (if configured).
        *   Secure Administrator Authentication.
    *   **Responsive Design:** Adapts to different screen sizes (mobile, tablet, desktop).

## Technical Stack

    *   **Backend:** Python, Flask
    *   **Database:** PostgreSQL (via SQLAlchemy and Flask-Migrate)
    *   **Frontend:** HTML5, CSS3, JavaScript
    *   **Templating:** Jinja2
    *   **Python Dependency Management:** pip, `requirements.txt`
    *   **Environment Variables:** python-dotenv
    *   **Deployment (Example):** Vercel

## Quick Start (Local)

    Follow these steps to set up and run the project on your local machine.

### Prerequisites

    *   Python 3.8+
    *   pip (usually included with Python)
    *   A running PostgreSQL server
    *   (Optional) Git to clone the repository

### Installation

    1.  **Clone the repository (if using Git):**
        ```bash
        git clone https://github.com/komythomas/artportfolio.git
        cd artportfolio
        ```

    2.  **Create and Activate a Virtual Environment:**
        ```bash
        # Windows
        python -m venv venv
        .\venv\Scripts\activate

        # macOS / Linux
        python3 -m venv venv
        source venv/bin/activate
        ```

    3.  **Install Python dependencies:**
        ```bash
        pip install -r requirements.txt
        ```

    4.  **Configure Environment Variables:**
        *   Create a `.env` file in the project root.
        *   Copy the contents of `.env.example` (if provided) or add the necessary variables. Minimal example:
            ```dotenv
            # .env
            FLASK_ENV=development
            SECRET_KEY='your_very_complex_secret_key_here' # Generate a secure key (e.g., python -c 'import secrets; print(secrets.token_hex(16))')
            DATABASE_URL='postgresql://user:password@host:port/database_name' # Adapt to your PostgreSQL config

            # Optional email variables (if configured)
            MAIL_SERVER='smtp.example.com'
            MAIL_PORT=587
            MAIL_USE_TLS=True
            MAIL_USERNAME='your_email@example.com'
            MAIL_PASSWORD='your_email_password'
            ADMIN_EMAIL='email_destination@example.com'

            # Other specific variables (if needed)
            # VERCEL_BLOB_RW_TOKEN= # Required only if deployed on Vercel with Blob Storage
            ```
        *   **Important:** Ensure the database specified in `DATABASE_URL` exists on your PostgreSQL server.

    5.  **Initialize and Migrate the Database:**
        *   Make sure the environment variables are loaded (activating the venv might be sufficient, otherwise restart your terminal).
        *   Apply the migrations:
            ```bash
            flask db upgrade
            ```
        *   *Note:* If this is the very first time and there is no `migrations` folder, you might need to initialize: `flask db init`, then create an initial migration: `flask db migrate -m "Initial migration"` before running `flask db upgrade`.

    6.  **Create an Administrator User (if necessary):**
        *   The project might include a Flask command for this, or you might need to add it manually to the database or via a secure initial registration route. Check the source code (e.g., in `portfolio/auth/routes.py` or custom Flask commands).
        *   Example command (if it exists):
            ```bash
            flask create-admin --username=admin --password=yoursecurepassword
            ```

### Run the Application

    ```bash
    flask run
    ```

    The application should be accessible at `http://127.0.0.1:5000` (or another port if specified).

## Usage

    *   Browse the site to see the different sections (Home, Gallery, About, Commissions, Contact).
    *   Access the admin panel via `/admin/login` or `/admin` if you have configured a specific route for administration. You will need to be authenticated with administrator credentials to access this panel. Log in with the admin credentials to manage the content.

## Deployment

    This project is configured for easy deployment on Vercel:

    1.  **Push your code to GitHub/GitLab/Bitbucket.**
    2.  **Connect your Git repository to Vercel.**
    3.  **Vercel Configuration:**
        *   Vercel should detect Python and use `vercel.json`.
        *   The **Build Command** should be `pip install -r requirements.txt`.
        *   The **Output Directory** is generally not needed.
        *   The framework must be Python, and the entry point (`wsgi.py`) will be used.
    4.  **Environment Variables:** Configure **all** necessary variables (those from your local `.env`, plus `FLASK_ENV=production`) in the Vercel project settings. **Never commit your `.env` file!**
    5.  **Deploy.** Vercel will handle the build and deployment.
    6.  **Database Migrations:** Migrations (`flask db upgrade`) must be run **manually** or via a separate CI/CD process **after** deployment, targeting your production database. They should **not** be part of the Vercel build process.

## Contributing (Optional)

    Contributions are welcome! Please read `CONTRIBUTING.md` for details on our code of conduct and the process for submitting pull requests. Contributions are appreciated and encouraged.

## License (Optional)

    This project is licensed under the MIT License - see the `LICENSE.md` file for details.

## Contact

    *   [Contact me](mailto:komythomas@gmail.com) for any questions or suggestions.
        ```