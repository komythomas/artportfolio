# Contribution Guide

    Thank you for your interest in contributing to the Art Portfolio project! All contributions, whether bug reports, feature suggestions, or code, are welcome and appreciated.

## Code of Conduct

    This project and everyone participating in it are governed by our [Code of Conduct](CODE_OF_CONDUCT.md) (to be created if necessary). By participating, you agree to uphold this code. Please report unacceptable behavior to [komythomas@gmail.com].

## How to Contribute?

    There are several ways to contribute:

### 1. Reporting Bugs

    *   **Check Existing Issues:** Before submitting a new bug report, please check if a similar report already exists in the [Issues](https://github.com/komythomas/artportfolio/issues) section of the GitHub repository.
    *   **Open a New Issue:** If the bug is not already reported, open a new issue. Be sure to include:
        *   A clear and descriptive title.
        *   A detailed description of the steps to reproduce the bug.
        *   The expected behavior.
        *   The observed behavior (including error messages or screenshots if relevant).
        *   Your environment (browser version, operating system, Python version, etc.).

### 2. Suggesting Enhancements or New Features

    *   **Check Existing Issues:** See if a similar suggestion has already been made in the [Issues](https://github.com/komythomas/artportfolio/issues).
    *   **Open a New Issue:** If not, open a new issue clearly describing:
        *   The desired feature or proposed enhancement.
        *   The problem it would solve or the value it would add.
        *   (Optional) Suggestions on how to implement it.

### 3. Submitting Pull Requests (PRs)

    Code contributions are welcome!

    1.  **Fork the Repository:** Create a copy (fork) of the main repository (`komythomas/artportfolio`) to your own GitHub account.
    2.  **Clone Your Fork:** Clone your fork to your local machine:
        ```bash
        git clone https://github.com/komythomas/artportfolio.git
        cd artportfolio
        ```
        *(Replace `YOUR_USERNAME` with your actual GitHub username)*
    3.  **Create a Branch:** Create a new branch for your changes. Use a descriptive name (e.g., `fix/gallery-bug` or `feature/add-artwork-sorting`).
        ```bash
        git checkout -b your-branch-name
        ```
    4.  **Set Up Development Environment:** Follow the instructions in the "Quick Start (Local)" section of the `README.md` file to install dependencies and configure the database.
    5.  **Make Changes:** Write your code, fix the bug, or implement the feature.
        *   Adhere to the existing code style.
        *   Add tests if relevant.
        *   Update documentation if necessary.
    6.  **Test Your Changes:** Ensure your changes do not introduce new problems and that existing tests (if any) still pass.
    7.  **Commit Your Changes:** Make clear and concise commits.
        ```bash
        git add .
        git commit -m "Fix: Correct image display in the gallery"
        # Or
        git commit -m "Feat: Add ability to sort artworks by date"
        ```
    8.  **Push to Your Fork:** Send your changes to your fork on GitHub.
        ```bash
        git push origin your-branch-name
        ```
    9.  **Open a Pull Request:**
        *   Go to your fork's page on GitHub.
        *   Click on "Compare & pull request".
        *   Ensure the base branch is `main` (or the primary branch of the `komythomas/artportfolio` repository) and the compare branch is `your-branch-name` from your fork.
        *   Provide a clear title for your PR and a detailed description of the changes you made. Link the corresponding issue if it exists (e.g., `Closes #123`).
        *   Submit the Pull Request.

## Review Process

    *   A maintainer will review your PR. Comments or requests for changes may be made.
    *   Once approved, your PR will be merged into the main branch.

    Thank you for your contribution!
    ```