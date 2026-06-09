from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, disconnect
import cv2
import numpy as np
import base64
import collections
from datetime import datetime
from fer import FER

app = Flask(__name__)
app.config['SECRET_KEY'] = 'classroom_secret'

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

detector = FER(mtcnn=False)

students = {}
session_log = {}
session_meta = {
    'start_time': None,
    'end_time': None,
    'class_name': 'My Class',
    'room': 'Room 101',
}
last_session_snapshot = {}

# Dynamic timeline: list of {'attentive': int, 'not_attentive': int, 'label': str}
timeline_data = []
kicked_students = set()

NEGATIVE_EMOTIONS = {'sad', 'angry', 'fear', 'disgust'}

EMOTION_EMOJI = {
    'happy':    '😊 Happy',
    'neutral':  '😐 Neutral',
    'sad':      '😢 Sad',
    'angry':    '😠 Angry',
    'fear':     '😨 Fearful',
    'surprise': '😲 Surprised',
    'disgust':  '🤢 Disgusted',
}


def detect_attention(base64_image: str):
    try:
        img_data = base64.b64decode(base64_image.split(',')[1])
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            return False, base64_image, "unknown"

        result = detector.detect_emotions(img)

        if not result:
            cv2.putText(img, "No face", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 60, 220), 2)
            cv2.rectangle(img, (0, 0), (img.shape[1]-1, img.shape[0]-1), (0, 60, 220), 3)
            _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 60])
            return False, "data:image/jpeg;base64," + base64.b64encode(buffer).decode(), "unknown"

        emotions = result[0]['emotions']
        emotion = max(emotions, key=emotions.get)
        attentive = emotion in ('happy', 'neutral', 'surprise', 'fear')

        x, y, w, h = result[0]['box']
        color = (0, 200, 80) if attentive else (0, 60, 220)
        cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)
        cv2.putText(img, f"{emotion} | {'Attentive' if attentive else 'Not Attentive'}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.rectangle(img, (0, 0), (img.shape[1]-1, img.shape[0]-1), color, 3)

        _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 60])
        return attentive, "data:image/jpeg;base64," + base64.b64encode(buffer).decode(), emotion

    except Exception as e:
        print(f"FER error: {e}")
        return False, base64_image, "unknown"


def get_elapsed_minutes() -> float:
    if not session_meta['start_time']:
        return 0
    return (datetime.now() - session_meta['start_time']).total_seconds() / 60


def get_bucket_index() -> int:
    """Get which 5-min bucket we are currently in."""
    elapsed = get_elapsed_minutes()
    return int(elapsed // 5)


def ensure_bucket(idx: int):
    """Make sure timeline_data has enough buckets up to idx."""
    while len(timeline_data) <= idx:
        start_min = len(timeline_data) * 5
        end_min = start_min + 5
        timeline_data.append({
            'attentive': 0,
            'not_attentive': 0,
            'label': f"{start_min}–{end_min}min"
        })


def format_duration(start, end) -> str:
    if not start or not end:
        return '—'
    total_sec = int((end - start).total_seconds())
    h, rem = divmod(total_sec, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h {m}m {s}s"
    elif m:
        return f"{m}m {s}s"
    return f"{s}s"


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/teacher')
def teacher():
    return render_template('teacher.html')

@app.route('/whiteboard')
def whiteboard():
    return render_template('whiteboard.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/report')
def report():
    return render_template('dashboard.html')

@app.route('/api/session/latest')
def session_latest():
    if not last_session_snapshot or not last_session_snapshot.get('students'):
        return jsonify({
            'students': [],
            'timeline': {'labels': [], 'attentive': [], 'notAttentive': []},
            'totalAlerts': 0,
            'duration': '—',
            'className': '—',
            'room': '—'
        })
    return jsonify(last_session_snapshot)

@app.route('/api/session/reset')
def session_reset():
    global last_session_snapshot
    session_log.clear()
    kicked_students.clear()
    timeline_data.clear()
    last_session_snapshot = {}
    session_meta['start_time'] = None
    session_meta['end_time'] = None
    return jsonify({'status': 'reset'})


# ── Socket Events ─────────────────────────────────────────────────────────────

@socketio.on('student_join')
def on_student_join(data):
    if request.sid in kicked_students:
        disconnect(request.sid)
        return

    name = data.get('name', 'Unknown')
    students[request.sid] = name

    # Start session clock only on very first student of a NEW session
    if session_meta['start_time'] is None:
        session_meta['start_time'] = datetime.now()
        session_meta['end_time'] = None
        timeline_data.clear()
        print(f"[SESSION] Started at {session_meta['start_time']}")

    if request.sid not in session_log:
        session_log[request.sid] = {
            'name': name,
            'join_time': datetime.now(),
            'alerts': 0,
            'emotions': [],
            'attentive_frames': 0,
            'total_frames': 0,
            'attentive': False,
        }

    print(f"[JOIN] {name} ({request.sid})")
    emit('student_joined', {'sid': request.sid, 'name': name}, broadcast=True)


@socketio.on('disconnect')
def on_disconnect():
    name = students.pop(request.sid, 'Unknown')
    # Mark as left early in session log
    if request.sid in session_log:
        session_log[request.sid]['left_early'] = True
    print(f"[LEAVE] {name} ({request.sid})")
    emit('student_left', {'sid': request.sid}, broadcast=True)

@socketio.on('teacher_audio')
def on_teacher_audio(data):
    emit('teacher_audio', data, broadcast=True, include_self=False)

@socketio.on('teacher_mic_stop')
def on_teacher_mic_stop():
    emit('teacher_mic_stop', broadcast=True, include_self=False)


    
@socketio.on('frame')
def on_frame(data):
    sid = request.sid
    if sid in kicked_students:
        disconnect(sid)
        return

    name = students.get(sid, 'Unknown')
    attentive, annotated, emotion = detect_attention(data.get('frame'))
    emotion_lower = (emotion or '').lower()
    emotion_label = EMOTION_EMOJI.get(emotion_lower, '❓ Unknown')

    if sid not in session_log:
        session_log[sid] = {
            'name': name, 'join_time': datetime.now(), 'alerts': 0,
            'emotions': [], 'attentive_frames': 0,
            'total_frames': 0, 'attentive': attentive, 'left_early': False
        }

    log = session_log[sid]
    log['name'] = name
    log['emotions'].append(emotion_lower)
    log['total_frames'] += 1
    if attentive:
        log['attentive_frames'] += 1
    log['attentive'] = attentive
    if emotion_lower in NEGATIVE_EMOTIONS or not attentive:
        log['alerts'] += 1

    # Update dynamic timeline bucket
    bucket_idx = get_bucket_index()
    ensure_bucket(bucket_idx)
    if attentive:
        timeline_data[bucket_idx]['attentive'] += 1
    else:
        timeline_data[bucket_idx]['not_attentive'] += 1

    emit('student_frame', {
        'sid': sid, 'name': name, 'frame': annotated,
        'attentive': attentive, 'emotion': emotion_label
    }, broadcast=True)

    if emotion_lower in NEGATIVE_EMOTIONS or not attentive:
        emit('teacher_alert', {'sid': sid, 'name': name,
                               'emotion': emotion, 'attentive': attentive}, broadcast=True)


# ── Whiteboard ────────────────────────────────────────────────────────────────

@socketio.on('wb_stroke')
def on_wb_stroke(data):
    emit('wb_stroke', data, broadcast=True, include_self=False)

@socketio.on('wb_clear')
def on_wb_clear():
    emit('wb_clear', broadcast=True, include_self=False)


# ── End Class ─────────────────────────────────────────────────────────────────

@socketio.on('end_class')
def on_end_class():


    global last_session_snapshot

    end_time = datetime.now()
    session_meta['end_time'] = end_time

    # Build student list
    students_snapshot = []
    for sid, d in session_log.items():
        dom_emotion = collections.Counter(d['emotions']).most_common(1)
        dom_emotion = dom_emotion[0][0] if dom_emotion else 'neutral'
        total = d['total_frames'] or 1
        score = round((d['attentive_frames'] / total) * 100)
        students_snapshot.append({
            'name': d['name'],
            'attentive': score >= 50,
            'emotion': dom_emotion,
            'alerts': d['alerts'],
            'score': score,
            'left_early': d.get('left_early', False)
        })

    # Build timeline using only actual buckets used
    tl_labels = [b['label'] for b in timeline_data]
    tl_att    = [b['attentive'] for b in timeline_data]
    tl_not    = [b['not_attentive'] for b in timeline_data]

    last_session_snapshot = {
        'className': session_meta['class_name'],
        'room':      session_meta['room'],
        'duration':  format_duration(session_meta['start_time'], end_time),
        'students':  students_snapshot,
        'totalAlerts': sum(d['alerts'] for d in session_log.values()),
        'timeline': {
            'labels':       tl_labels,
            'attentive':    tl_att,
            'notAttentive': tl_not,
        }
    }

    # Reset for next class
    session_log.clear()
    kicked_students.clear()
    timeline_data.clear()
    session_meta['start_time'] = None
    session_meta['end_time'] = None

    emit('class_ended', broadcast=True)


# ── Kick Student ──────────────────────────────────────────────────────────────

@socketio.on('kick_student')
def kick_student(data):
    sid = data.get('sid')
    if sid:
        kicked_students.add(sid)
        students.pop(sid, None)
        print(f"[KICKED] {sid}")
        emit('force_disconnect', {}, room=sid)
        disconnect(sid)
        emit('student_left', {'sid': sid}, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5500, debug=False)
