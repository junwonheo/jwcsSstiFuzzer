# 1) 베이스 이미지
FROM python:3.12-slim-bookworm

# 2) 작업 디렉터리
WORKDIR /app

# 3) 의존성 목록 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) 애플리케이션 코드 복사
COPY . .

# 5) Flask 환경 변수 설정
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_DEBUG=1

# 6) 외부에 노출할 포트
EXPOSE 5000

# 7) 컨테이너 시작 시 Flask 내장 서버 실행
CMD ["flask", "run"]
