import cv2
import requests
import numpy as np
from flask import Flask, render_template, jsonify, Response, request
import mysql.connector
from mysql.connector import Error
from datetime import datetime

app = Flask(__name__, static_folder='templates')

# 데이터베이스 설정
db_config = {
    'user': 'root',
    'password': '1111',
    'host': 'localhost',
    'database': 'sw_project',
}

# ESP32-CAM의 IP 주소
STREAM_URL = "http://192.168.45.85:81/stream"

# 얼굴 감지 모델 로드
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("MySQL 데이터베이스에 성공적으로 연결되었습니다.")
    except Error as e:
        print(f"에러 '{e}' 발생")
    return connection

def insert_record(connection, count, date_time, age, gender):
    cursor = connection.cursor()
    query = "INSERT INTO camera_sw1 (count, date_time, age, gender) VALUES (%s, %s, %s, %s)"
    values = (count, date_time, age, gender)
    cursor.execute(query, values)
    connection.commit()

def generate():
    connection = create_connection()
    stream = requests.get(STREAM_URL, stream=True)
    byte_data = bytes()
    face_count = 0
    face_detected = False

    for chunk in stream.iter_content(chunk_size=1024):
        byte_data += chunk
        a = byte_data.find(b'\xff\xd8')
        b = byte_data.find(b'\xff\xd9')
        if a != -1 and b != -1:
            jpg = byte_data[a:b+2]
            byte_data = byte_data[b+2:]

            if jpg:
                img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                if img is not None:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

                    current_face_detected = len(faces) > 0
                    for (x, y, w, h) in faces:
                        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

                    if face_detected and not current_face_detected:
                        face_count += 1
                        date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        insert_record(connection, face_count, date_time, 0, 'unknown')

                    face_detected = current_face_detected
                    _, jpeg = cv2.imencode('.jpg', img)
                    frame = jpeg.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    if connection.is_connected():
        connection.close()

@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# 홈 페이지 라우트
@app.route('/')
def index():
    return render_template('index.html')

# 얼굴 인식 데이터 API 라우트
@app.route('/face_counts')
def get_face_counts():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        today = request.args.get('today')

        if today:
            query = "SELECT date_time, count, age, gender FROM camera_sw1 WHERE DATE(date_time) = CURDATE()"
            cursor.execute(query)
        elif start_date and end_date:
            query = "SELECT date_time, count, age, gender FROM camera_sw1 WHERE date_time BETWEEN %s AND %s"
            cursor.execute(query, (start_date, end_date))
        else:
            cursor.execute('SELECT date_time, count, age, gender FROM camera_sw1')

        rows = cursor.fetchall()
        cursor.close()
        connection.close()

        data = [{'date_time': row[0].strftime('%Y-%m-%d %H:%M:%S'), 'count': row[1], 'age': row[2], 'gender': row[3]} for row in rows]
        return jsonify(data)
    except Error as err:
        print(f"Database Error: {err}")
        return jsonify({"error": str(err)}), 500

    except Exception as e:
        print(f"Unexpected Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
