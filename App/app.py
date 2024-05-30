from flask import Flask, render_template, request, redirect, url_for, session
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
import os

app = Flask(__name__)
app.secret_key = "abobaaaa"

model = load_model("../Model/BrainTumor.keras")


def prepare_image(img_path):
    img = Image.open(img_path)
    img = img.resize((128, 128))
    img = np.array(img)
    if img.shape[-1] == 4: 
        img = img[..., :3]
    img = img / 255.0
    img = np.expand_dims(img, axis=0) 
    return img


def clear_session():
    if 'img_path' in session:
        img_path = session['img_path']
        if os.path.exists(img_path):
            os.remove(img_path)
        session.pop('img_path', None)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            clear_session()
            file_path = os.path.join("static/cache", file.filename)
            file.save(file_path)
            img = prepare_image(file_path)
            prediction = model.predict(img)
            result = "Tumor" if prediction[0][0] > 0.5 else "No Tumor"
            session['img_path'] = file_path
            return render_template('index.html', result=result, img_path=file_path)
    return render_template('index.html', result=None, img_path=session.get('img_path'))


if __name__ == "__main__":
    app.run(debug=True)
