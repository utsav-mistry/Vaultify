# Vaultify

Welcome to **Vaultify**! This is a secure and efficient Flask-based password management system designed to help users store, organize, and manage their passwords and OTPs with ease. Vaultify focuses on user security, modern design, and seamless deployment.

## Features

- **Secure Password Storage**: Safely store and manage your passwords using encryption.
- **OTP Management**: Generate and manage one-time passwords (OTP) for two-factor authentication.
- **User-Friendly Interface**: Modern and intuitive UI designed with simplicity in mind.
- **Dark Mode Support**: Toggle between light and modern dark mode for a better user experience.


## Requirements

This project requires Python and several dependencies. To run it locally, follow the steps below.

- Python 3.x
- Virtual Environment (recommended)
- Flask
- Additional dependencies listed in `requirements.txt`

## Setup Instructions

1. Clone the repository:

    ```bash
    git clone https://github.com/utsav-mistry/Vaultify.git
    ```

2. Navigate into the project folder:

    ```bash
    cd password_manager
    ```

3. Create a virtual environment (if you don’t have one already):

    ```bash
    python3 -m .venv venv
    ```

4. Activate the virtual environment:

    - On Windows:

        ```bash
        .venv\Scripts\activate
        ```

    - On Mac/Linux:

        ```bash
        source .venv/bin/activate
        ```

5. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```



6. Run the app:

    ```bash
    flask run
    ```


## Deployment on Vercel

To deploy Vaultify to Vercel, follow these steps:

1. Push your changes to GitHub (or your Git repository).
2. Connect your GitHub repository to Vercel.
3. Configure the necessary environment variables in Vercel for secure operations (e.g., `FLASK_SECRET_KEY`, `DATABASE_URL`, etc.).
4. Vercel will automatically detect Flask and install the dependencies from `requirements.txt`.

For more detailed instructions, refer to the [Vercel Documentation](https://vercel.com/docs).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

## Acknowledgments

- Thanks to [Flask](https://palletsprojects.com/p/flask/) for the web framework.
- Thanks to [Vercel](https://vercel.com) for seamless deployment.
- Thanks to the open-source community for inspiring the development of `Vaultify`.