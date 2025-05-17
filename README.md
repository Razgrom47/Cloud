
# Mini Cloud Flask App

A simple, lightweight cloud storage web application built with Flask.  
Allows you to browse, upload, create folders, delete files/folders, and search within your cloud storage directory. Includes a light/dark theme toggle.

---

## Features

- Browse files and folders stored in the local `cloud_storage` directory.
- Upload multiple files with allowed extensions.
- Create new folders.
- Delete selected files or folders.
- Search files and folders recursively.
- Serve files securely with path sanitization.
- Toggle between light and dark themes.
- Disk usage display for the storage directory.
- Flash messages for user feedback.

---

## Folder Structure

```
D:.
├───.venv                    # Python virtual environment
├───cloud_storage            # Main storage directory (changeable in config)
│   └───Veni                 # Example subfolder
├───static                   # Static files (CSS, JS)
├───templates                # HTML templates
└───uploads                  # (Optional) Upload folder if used separately
```

---

## Requirements

- Python 3.8+
- Flask
- Werkzeug

Install dependencies using:

```bash
pip install flask werkzeug
```

---

## Setup & Running

1. Clone or download this repository.
2. Create and activate a Python virtual environment (recommended):

   ```bash
   python -m venv .venv
   source .venv/Scripts/activate  # Windows
   source .venv/bin/activate      # Linux / Mac
   ```

3. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Ensure the folder `cloud_storage` exists in the project root, or update `BASE_DIR` in the app code to your desired storage path.

5. Run the app:

   ```bash
   python app.py
   ```

6. Open your browser at `http://127.0.0.1:5000/`

---

## Usage

- Navigate folders by clicking folder names.
- Upload files via the upload form (multiple files supported).
- Create folders via the folder creation form.
- Select files/folders to delete using checkboxes and the action dropdown.
- Search files or folders by typing in the search box.
- Toggle light/dark theme with the toggle button.

---

## Configuration

- `BASE_DIR`: Change the base directory where files are stored.
- `ALLOWED_EXTENSIONS`: Modify allowed upload file types.

---

## Security Notes

- The app restricts file serving and actions strictly inside the `BASE_DIR` folder to prevent directory traversal.
- Uploaded filenames are sanitized using Werkzeug's `secure_filename`.
- No authentication implemented — use in trusted environments or extend with user login.

---

## Future Improvements

- Add user authentication and multi-user support.
- Enable file download compression (e.g., zip multiple files).
- Add file preview for images and PDFs.
- Pagination for folders with many files.
- Add more granular permissions and roles.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Author

Your Name — your.email@example.com  
GitHub: [yourusername](https://github.com/yourusername)

---

Feel free to customize this app and contribute improvements!
