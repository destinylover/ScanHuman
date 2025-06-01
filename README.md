# ScanHuman


제가 맡은 백엔드 구현 파트는 다음과 같습니다.

실시간 영상 스트리밍 처리

ESP32-CAM에서 MJPEG 스트림을 받아 OpenCV를 통해 프레임을 디코딩하고, 얼굴을 감지하도록 구현했습니다.

얼굴이 화면에서 사라질 때마다 인식 횟수(count)를 증가시키고, 날짜와 함께 DB에 저장했습니다.

MySQL 연동 및 데이터 저장 기능

camera_sw1 테이블에 얼굴 인식 결과(count, date_time, age, gender)를 저장하는 insert 함수를 직접 구현했습니다.

MySQL 연결 및 커넥션 생성 함수도 직접 작성했습니다.

REST API 구현

/video_feed 엔드포인트를 통해 실시간 영상 스트리밍을 웹에서 볼 수 있도록 구현했습니다.

/face_counts API를 통해 특정 날짜 또는 기간에 해당하는 얼굴 인식 기록을 JSON 형식으로 조회할 수 있도록 만들었습니다.

예외 처리 및 안정성 고려

DB 연결 실패나 쿼리 오류 발생 시 예외 처리를 추가해 서버가 안정적으로 동작하도록 구성했습니다.

커넥션을 요청 단위로 열고 닫아 리소스 누수를 방지했습니다.

기본 웹페이지 연동

/ 경로에서 index.html을 렌더링하여 프론트엔드와의 연결도 구성했습니다.


I was responsible for implementing the backend of this project. Here's what I worked on:

Real-Time Video Streaming and Face Detection

I connected to the ESP32-CAM’s MJPEG stream and decoded each frame using OpenCV.

Using Haar Cascade, the system detects faces in real time.

Each time a face is detected and then disappears, the count is increased, and the event is recorded in the database with a timestamp.

MySQL Integration and Data Storage

I implemented an insert function to store face detection data (count, date_time, age, gender) into the camera_sw1 table.

The age is temporarily stored as 0 and gender as 'unknown'.

I also created a custom function to establish a MySQL connection.

REST API Development

The /video_feed endpoint serves the live video stream to the frontend using multipart MJPEG format.

The /face_counts endpoint returns face detection records in JSON format, supporting filters by date range or current day.

Error Handling and Connection Stability

I added error handling for database connection failures and SQL execution issues to ensure reliable backend performance.

The database connection is opened and properly closed after each stream or API request to avoid resource leaks.

Frontend Integration

The root route / renders index.html to connect the frontend with the backend system.

