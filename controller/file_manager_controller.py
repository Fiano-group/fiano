import os

from flask import redirect, render_template, request
from modules import app
from modules.utils import file_utils as fu
from werkzeug.utils import secure_filename


@app.route("/upload", methods=['POST'])
def uploader():
    global filename
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        f = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename
        if f.filename == '':
            return redirect(request.url)
        if f and fu.allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            local_filename = 'static/' + filename
            return render_template('index.html', filename=local_filename)
