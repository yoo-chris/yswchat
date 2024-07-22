from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from flask_pymongo import PyMongo
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yswchat'
app.config["MONGO_URI"] = "mongodb://localhost:27017/chatDB"  # MongoDB URI 설정
socketio = SocketIO(app)
mongo = PyMongo(app)

# 메인 페이지 렌더링
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    return render_template('index2.html')

# 이전 채팅 메시지 가져오기
@app.route('/get_chats')
def get_chats():
    try:
        # MongoDB에서 모든 채팅 메시지를 가져와 JSON으로 반환 (최신 순으로 정렬)
        chats = mongo.db.chats.find()
        return jsonify([{
            'username': chat['username'],
            'msg': chat['message'],
            'timestamp': chat['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        } for chat in chats])
    except Exception as e:
        return str(e)

# 사용자별 채팅 내역 조회 (index2.html에서 사용)
@app.route('/get_user_chats/<username>')
def get_user_chats(username):
    try:
        # MongoDB에서 특정 사용자(username)의 채팅 메시지를 가져와 JSON으로 반환
        chats = mongo.db.chats.find({'username': username})
        return jsonify([{
            'username': chat['username'],
            'msg': chat['message'],
            'timestamp': chat['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        } for chat in chats])
    except Exception as e:
        return str(e)

# 소켓 이벤트 처리
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('message')
def handle_message(data):
    # 현재 시간을 가져와서 ISO 포맷으로 변환
    timestamp = datetime.utcnow()
    # 메시지를 MongoDB에 저장
    mongo.db.chats.insert_one({
        'username': data['username'],
        'message': data['msg'],
        'timestamp': timestamp
    })
    # 클라이언트에게 메시지와 시간 전송
    emit('message', {
        'username': data['username'],
        'msg': data['msg'],
        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
