from flask import Flask, render_template, request, send_file, send_from_directory, redirect, url_for, abort, session, flash
import os, zipfile, shutil
from werkzeug.utils import secure_filename
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'top-secret-key'

BASE_DIR = os.path.abspath("cloud_storage")
# You can now upload *any* file type:
# ALLOWED_EXTENSIONS is no longer used for upload filtering.
PREVIEW_EXTENSIONS = {'.txt', '.md', '.py', '.json', '.csv'}

@app.route('/files/<path:filename>')
def serve_files(filename):
    safe_path = os.path.abspath(os.path.join(BASE_DIR, filename))
    if not safe_path.startswith(BASE_DIR):
        abort(403)
    return send_from_directory(BASE_DIR, filename)

@app.route('/toggle_theme')
def toggle_theme():
    current = session.get('theme', 'light')
    session['theme'] = 'dark' if current == 'light' else 'light'
    return redirect(request.referrer or url_for('index'))

@app.route('/', defaults={'req_path': ''})
@app.route('/<path:req_path>')
def index(req_path):
    abs_path = os.path.join(BASE_DIR, req_path)
    if not os.path.exists(abs_path):
        return "Path does not exist", 404

    # -- Search or list folders/files --
    search = request.args.get('search', '').lower()
    if search:
        matched_folders, matched_files = [], []
        for root, dirs, files in os.walk(abs_path):
            rel = os.path.relpath(root, abs_path)
            rel = '' if rel == '.' else rel
            for d in dirs:
                if search in d.lower():
                    matched_folders.append(os.path.join(rel, d) if rel else d)
            for f in files:
                if search in f.lower():
                    matched_files.append(os.path.join(rel, f) if rel else f)
        folders, files = sorted(matched_folders), sorted(matched_files)
    else:
        items  = os.listdir(abs_path)
        folders = sorted([i for i in items if os.path.isdir(os.path.join(abs_path, i))])
        files   = sorted([i for i in items if os.path.isfile(os.path.join(abs_path, i))])

    # -- Build safe previews for text files only --
    file_previews = {}
    for f in files:
        path = os.path.join(abs_path, f)
        ext  = os.path.splitext(f)[1].lower()
        # also treat a top-level 'Dockerfile' as text
        if ext in PREVIEW_EXTENSIONS or f.lower() == 'dockerfile':
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                    file_previews[f] = fp.read(500)
            except Exception as e:
                file_previews[f] = f"❌ Error reading file: {e}"
        else:
            # unsupported types get no preview
            file_previews[f] = None

    total, used, _ = shutil.disk_usage(BASE_DIR)
    if 'visited' not in session:
        flash("👋 Welcome to your mini cloud!")
        session['visited'] = True

    return render_template(
        "index.html",
        folders=folders,
        files=files,
        file_previews=file_previews,
        current_path=req_path,
        BASE_DIR=BASE_DIR,
        theme=session.get('theme', 'light'),
        total=total,
        used=used
    )

@app.route('/upload', methods=['POST'])
def upload():
    dest = os.path.join(BASE_DIR, request.form.get('path', ''))
    for file in request.files.getlist('files'):
        if file and file.filename:
            name = secure_filename(file.filename)
            target = os.path.join(dest, name)
            if os.path.exists(target):
                flash(f"⚠️ File '{name}' already exists!")
            else:
                file.save(target)
                flash(f"✅ File '{name}' uploaded.")
    return redirect(url_for('index', req_path=request.form.get('path', '')))

@app.route('/mkdir', methods=['POST'])
def mkdir():
    path   = request.form.get('path', '')
    name   = secure_filename(request.form.get('foldername', ''))
    target = os.path.join(BASE_DIR, path, name)
    if not name:
        flash("❌ Folder name cannot be empty.")
    elif os.path.exists(target):
        flash(f"⚠️ Folder '{name}' already exists!")
    else:
        os.makedirs(target)
        flash(f"✅ Folder '{name}' created.")
    return redirect(url_for('index', req_path=path))

@app.route('/action', methods=['POST'])
def action():
    path = request.form.get('path', '')
    sel  = request.form.getlist('selected')
    act  = request.form.get('action_type')
    base = os.path.abspath(os.path.join(BASE_DIR, path))

    if not sel:
        flash("⚠️ No items selected.")
        return redirect(url_for('index', req_path=path))

    if act == 'delete':
        for item in sel:
            tgt = os.path.abspath(os.path.join(base, item))
            if not tgt.startswith(BASE_DIR):
                flash(f"⚠️ Invalid delete: {item}")
                continue
            try:
                if os.path.isdir(tgt):
                    shutil.rmtree(tgt)
                else:
                    os.remove(tgt)
                flash(f"✅ Deleted '{item}'.")
            except Exception as e:
                flash(f"❌ Could not delete '{item}': {e}")
        return redirect(url_for('index', req_path=path))

    if act == 'download':
        buf = BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
            for item in sel:
                tgt = os.path.abspath(os.path.join(base, item))
                if not tgt.startswith(BASE_DIR):
                    continue
                if os.path.isdir(tgt):
                    for r, _, fs in os.walk(tgt):
                        for f in fs:
                            src = os.path.join(r, f)
                            arc = os.path.relpath(src, base)
                            z.write(src, arcname=arc)
                else:
                    arc = os.path.relpath(tgt, base)
                    z.write(tgt, arcname=arc)
        buf.seek(0)
        return send_file(buf, download_name="mini-cloud.zip", as_attachment=True)

    return redirect(url_for('index', req_path=path))

if __name__ == "__main__":
    os.makedirs(BASE_DIR, exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)