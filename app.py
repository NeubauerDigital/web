from flask import Flask, render_template, request, send_from_directory
import os
import cv2

app = Flask(__name__)

# Carpeta para guardar imágenes subidas
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Crear carpeta si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No se encontró el archivo", 400

    file = request.files['file']

    if file.filename == '':
        return "No se seleccionó ningún archivo", 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # Procesamiento de la imagen con OpenCV
    image = cv2.imread(filepath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detección de círculos (células) con HoughCircles
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=20,
        param1=50,
        param2=30,
        minRadius=5,
        maxRadius=30
    )

    # Conteo con condición: solo círculos dentro del área útil (evita bordes)
    count = 0
    if circles is not None:
        height, width = gray.shape
        margen = 10  # píxeles desde el borde

        for circle in circles[0]:
            x, y, r = circle
            if margen < x < (width - margen) and margen < y < (height - margen):
                count += 1

    return render_template(
        'index.html',
        resultado=f"✅ Imagen subida correctamente.<br>🧫 Células detectadas dentro del área: {count}",
        imagen_url=f"/uploads/{file.filename}"
    )

# Ruta para mostrar la imagen subida
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
