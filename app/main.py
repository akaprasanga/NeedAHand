from flask import send_from_directory, Response
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import render_template
from url_utils import get_base_url
import os
import torch

import threading
import pyautogui
import cv2

# setup the webserver
# port may need to be changed if there are multiple flask servers running on same server
port = 12347
base_url = get_base_url(port)
video = cv2.VideoCapture(0)

# if the base url is not empty, then the server is running in development, and we need to specify the static folder so that the static files are served
if base_url == '/':
    app = Flask(__name__)
else:
    app = Flask(__name__, static_url_path=base_url+'static')

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

model = torch.hub.load("ultralytics/yolov5", "custom", path = 'best.pt', force_reload=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route(f'{base_url}', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))

    return render_template('index.html')


@app.route(f'{base_url}/uploads/<filename>')
def uploaded_file(filename):
    here = os.getcwd()
    image_path = os.path.join(here, app.config['UPLOAD_FOLDER'], filename)
    results = model(image_path, size=416)
    if len(results.pandas().xyxy) > 0:
        results.print()
        save_dir = os.path.join(here, app.config['UPLOAD_FOLDER'])
        results.save(save_dir=save_dir)
        def and_syntax(alist):
            if len(alist) == 1:
                alist = "".join(alist)
                return alist
            elif len(alist) == 2:
                alist = " and ".join(alist)
                return alist
            elif len(alist) > 2:
                alist[-1] = "and " + alist[-1]
                alist = ", ".join(alist)
                return alist
            else:
                return
        confidences = list(results.pandas().xyxy[0]['confidence'])
        # confidences: rounding and changing to percent, putting in function
        format_confidences = []
        for percent in confidences:
            format_confidences.append(str(round(percent*100)) + '%')
        format_confidences = and_syntax(format_confidences)

        labels = list(results.pandas().xyxy[0]['name'])
        # labels: sorting and capitalizing, putting into function
        labels = set(labels)
        labels = [emotion.capitalize() for emotion in labels]
        labels = and_syntax(labels)
        print(labels)
        return render_template('index.html', confidences=format_confidences, labels=labels,
                               old_filename=filename,
                               filename=filename, found = True)
    else:
        found = False
        return render_template('index.html', labels='No Gesture', old_filename=filename, filename=filename, found = False)
    
@app.route(f'{base_url}/uploads/<filename>', methods=['GET', 'POST'])
def uploaded_file_post(filename):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))

    return render_template('index.html')

@app.route(f'{base_url}/uploads/<path:filename>')
def files(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

# define additional routes here
# for example:
# @app.route(f'{base_url}/team_members')
# def team_members():
#     return render_template('team_members.html') # would need to actually make this page
def target_function(video):
    while True:
        success, image = video.read()
        # detected = "D:\AICamp\CrashCourse\HaarWebcam\static\yolov5"

        # results = model(image)
        results = model(image, size=416)
        # if len(results.pandas().xyxy) > 0:
        labels = list(results.pandas().xyxy[0]['name'])
        print("Detected:", labels)
        if len(labels) >0:
            if labels[0] == "Stop":
                pyautogui.press("s")
            elif labels[0] == "Left":
                pyautogui.press("d")
            elif labels[0] == "Right":
                pyautogui.press("a")
            elif labels[0] == "Up":
                pyautogui.press(" ")
            elif labels[0] == "Attack":
                pyautogui.click()
        # print("Results::", results)

                # encode the frame in JPEG format
        image = results.render()[0]
        (flag, encodedImage) = cv2.imencode(".jpg", image)
                # ensure the frame was successfully encoded

        # yield the output frame in the byte format
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(encodedImage) + b'\r\n')
#background process happening without any refreshing
@app.route('/background_process_test')
def background_process_test():
    t = threading.Thread(target=target_function(), name="name", args=video)
    t.daemon = True
    t.start()
    return ("nothing")

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(target_function(video),
		mimetype = "multipart/x-mixed-replace; boundary=frame")



if __name__ == '__main__':
    # IMPORTANT: change url to the site where you are editing this file.
    website_url = 'localhost'
    
    print(f'Try to open\n\n    https://{website_url}' + base_url + '\n\n')
    app.run(host = '0.0.0.0', port=port, debug=True)
