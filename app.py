from flask import Flask, render_template, request, send_file, send_from_directory, redirect, url_for, abort, session, flash
import os, zipfile, shutil
from werkzeug.utils import secure_filename
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'top-secret-key'
BASE_DIR = os.path.abspath("cloud_storage")
ALLOWED_EXTENSIONS = {'.txt', '.jpg', '.jpeg', '.png', '.pdf', '.docx', '.xlsx', '.md', '.csv', '.json', '.py'}

def is_allowed(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/files/<path:filename>')
def serve_files(filename):
    safe_path = os.path.abspath(os.path.join(BASE_DIR, filename))
    if not safe_path.startswith(BASE_DIR):
        abort(403)
    return send_from_directory(BASE_DIR, filename)

@app.route('/toggle_theme')
def toggle_theme():
    current_theme = session.get('theme', 'light')
    session['theme'] = 'dark' if current_theme == 'light' else 'light'
    return redirect(request.referrer or url_for('index'))

@app.route('/', defaults={'req_path': ''})
@app.route('/<path:req_path>')
def index(req_path):
    abs_path = os.path.join(BASE_DIR, req_path)
    if not os.path.exists(abs_path):
        return "Path does not exist", 404

    search = request.args.get('search', '').lower()

    if search:
        # Recursive search for matching files and folders under abs_path
        matched_folders = []
        matched_files = []
        for root, dirs, files in os.walk(abs_path):
            # relative path from abs_path to current root
            rel_root = os.path.relpath(root, abs_path)
            rel_root = '' if rel_root == '.' else rel_root

            # check folders
            for d in dirs:
                if search in d.lower():
                    # Build relative path from req_path + rel_root + d
                    folder_rel_path = os.path.join(rel_root, d) if rel_root else d
                    matched_folders.append(folder_rel_path)

            # check files
            for f in files:
                if search in f.lower():
                    file_rel_path = os.path.join(rel_root, f) if rel_root else f
                    matched_files.append(file_rel_path)

        # Sort results
        folders = sorted(matched_folders)
        files = sorted(matched_files)
    else:
        all_items = os.listdir(abs_path)
        folders = sorted([f for f in all_items if os.path.isdir(os.path.join(abs_path, f))])
        files = sorted([f for f in all_items if os.path.isfile(os.path.join(abs_path, f))])

    total, used, _ = shutil.disk_usage(BASE_DIR)

    if 'visited' not in session:
        flash("👋 Welcome to your mini cloud!")
        session['visited'] = True

    return render_template("index.html", folders=folders, files=files, current_path=req_path,
                           BASE_DIR=BASE_DIR, theme=session.get('theme', 'light'),
                           total=total, used=used)

@app.route('/upload', methods=['POST'])
def upload():
    path = request.form.get('path', '')
    upload_path = os.path.join(BASE_DIR, path)
    files = request.files.getlist('files')
    for file in files:
        if file and is_allowed(file.filename):
            filename = secure_filename(file.filename)
            full_path = os.path.join(upload_path, filename)
            if os.path.exists(full_path):
                flash(f"⚠️ File '{filename}' already exists!")
            else:
                file.save(full_path)
                flash(f"✅ File '{filename}' uploaded.")
        else:
            flash(f"❌ Unsupported file type: {file.filename}")
    return redirect(url_for('index', req_path=path))

@app.route('/mkdir', methods=['POST'])
def mkdir():
    path = request.form.get('path', '')
    folder_name = secure_filename(request.form.get('foldername', ''))
    full_path = os.path.join(BASE_DIR, path, folder_name)

    if not folder_name:
        flash("❌ Folder name cannot be empty.")
    elif os.path.exists(full_path):
        flash(f"⚠️ Folder '{folder_name}' already exists!")
    else:
        os.makedirs(full_path)
        flash(f"✅ Folder '{folder_name}' created.")
    return redirect(url_for('index', req_path=path))

@app.route('/action', methods=['POST'])
def action():
    path = request.form.get('path', '')
    selected = request.form.getlist('selected')
    action_type = request.form.get('action_type')

    if not selected:
        flash("⚠️ No items selected.")
        return redirect(url_for('index', req_path=path))

    if action_type == 'delete':
        base_folder = os.path.abspath(os.path.join(BASE_DIR, path))
        for item in selected:
            full_path = os.path.abspath(os.path.join(base_folder, item))

            # Security check: ensure path is inside BASE_DIR
            if not full_path.startswith(BASE_DIR):
                flash(f"⚠️ Attempt to delete outside allowed directory: {item}")
                continue

            if os.path.isdir(full_path):
                try:
                    shutil.rmtree(full_path)
                    flash(f"✅ Folder '{item}' deleted.")
                except Exception as e:
                    flash(f"❌ Failed to delete folder '{item}': {str(e)}")
            elif os.path.isfile(full_path):
                try:
                    os.remove(full_path)
                    flash(f"✅ File '{item}' deleted.")
                except Exception as e:
                    flash(f"❌ Failed to delete file '{item}': {str(e)}")
            else:
                flash(f"⚠️ Item '{item}' not found.")

        return redirect(url_for('index', req_path=path))

    elif action_type == 'download':
        # existing download code (unchanged)
        zip_stream = BytesIO()
        with zipfile.ZipFile(zip_stream, 'w', zipfile.ZIP_DEFLATED) as zipf:
            base_folder = os.path.abspath(os.path.join(BASE_DIR, path))
            for item in selected:
                full_path = os.path.abspath(os.path.join(base_folder, item))
                if not full_path.startswith(BASE_DIR):
                    continue  # Security: skip invalid paths
                if os.path.isdir(full_path):
                    for root, _, files in os.walk(full_path):
                        for f in files:
                            abs_file = os.path.join(root, f)
                            rel_path = os.path.relpath(abs_file, base_folder)
                            zipf.write(abs_file, arcname=rel_path)
                elif os.path.isfile(full_path):
                    rel_path = os.path.relpath(full_path, base_folder)
                    zipf.write(full_path, arcname=rel_path)
        zip_stream.seek(0)
        return send_file(zip_stream, download_name="mini-cloud.zip", as_attachment=True)

    return redirect(url_for('index', req_path=path))

if __name__ == "__main__":
    os.makedirs(BASE_DIR, exist_ok=True)
    app.run(debug=True)
