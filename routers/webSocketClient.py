from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Dev"])


@router.get("/test/ws")
async def websocket_echo_page():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Client</title>
    </head>
    <body>
        <div id="messages"></div>
        <script>
            const socket = new WebSocket("wss://sound.bs-soft.co.kr/ws");

            socket.onopen = function(event) {
                setInterval(function() {
                    const message = {data: "Hello, WebSocket!"};  // JSON 형식의 데이터 생성
                    socket.send(JSON.stringify(message));  // 데이터를 문자열로 직렬화하여 전송
                }, 1000);  // 1초마다 메시지 보내기
            };

            socket.onmessage = function(event) {
                const message = JSON.parse(event.data);  // 수신한 데이터를 JSON으로 파싱
                const messagesDiv = document.getElementById("messages");
                messagesDiv.innerHTML += `<p>${message.data}</p>`;  // JSON 데이터의 필드 접근
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(html)

@router.get("/receive/ws/byte")
async def print_received_websocket_message():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Client</title>
    </head>
    <body>
        <div id="messages"></div>
        <ul id="messag" style="list-style: none"></ul>
        <script>
            var socket = new WebSocket("wss://sound.bs-soft.co.kr/ws/byte");
            socket.onmessage = function(event) {
                const message = JSON.parse(event.data);  // 수신한 데이터를 JSON으로 파싱
                const messagesDiv = document.getElementById("messages");
                messagesDiv.innerHTML += `<p>${message.data}</p>`;  // JSON 데이터의 필드 접근
            };

        </script>
    </body>
    </html>
    """
    return HTMLResponse(html)
