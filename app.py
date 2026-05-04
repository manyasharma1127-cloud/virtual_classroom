from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import cv2
import numpy as np
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'classroom_secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Store connected students: { socket_id: name }
students = {}

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


def detect_attention(base64_image: str) -> tuple[bool, str]:
    """Decode base64 frame, run face detection, return (is_attentive, annotated_base64)."""
    try:
        img_data = base64.b64decode(base64_image.split(',')[1])
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            return False, base64_image

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

        attentive = len(faces) > 0

        for (x, y, w, h) in faces:
            color = (0, 200, 80) if attentive else (0, 60, 220)
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img, "Attentive" if attentive else "Not Attentive",
                        (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

        _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 60])
        annotated_b64 = "data:image/jpeg;base64," + base64.b64encode(buffer).decode('utf-8')

        return attentive, annotated_b64

    except Exception as e:
        print(f"Detection error: {e}")
        return False, base64_image


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/teacher')
def teacher():
    return render_template('teacher.html')


# ── Socket events ─────────────────────────────────────────────────────────────

@socketio.on('student_join')
def on_student_join(data):
    name = data.get('name', 'Unknown')
    students[request.sid] = name
    print(f"[JOIN] {name} ({request.sid})")
    # Notify teacher
    emit('student_joined', {'sid': request.sid, 'name': name}, broadcast=True)


@socketio.on('disconnect')
def on_disconnect():
    name = students.pop(request.sid, 'Unknown')
    print(f"[LEAVE] {name} ({request.sid})")
    emit('student_left', {'sid': request.sid}, broadcast=True)


@socketio.on('frame')
def on_frame(data):
    """Receive a frame from a student, run detection, forward to teacher."""
    sid = request.sid
    name = students.get(sid, 'Unknown')
    frame_b64 = data.get('frame')

    attentive, annotated = detect_attention(frame_b64)

    emit('student_frame', {
        'sid': sid,
        'name': name,
        'frame': annotated,
        'attentive': attentive
    }, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=5500, debug=False)
