from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from database import SoundData
from users import auth_backend, fastapi_users
import uvicorn, asyncio

import shutil, os, time
from utils.network import cors
from utils.log_conf import app_log_conf
from utils.ini import (config, models, stt_processors, ref_voice_shcho, ref_voice_bsjang)
from utils.webSocket import notifier
from utils.soundprocessor import stt, voice_recognition
from nlp.vocabraries import filter_forbidden
from routers import onestopAnalysis, webSocketClient

app = FastAPI(
    title="BSsoft Sound Processing Test",
    description="BS소프트의 사운드처리 테스트 API 페이지입니다. (로그인관리, 1파일사운드처리, STT)",
    version="2.0.0"
)

cors(app)

# fastapi-users 모듈 include (회원가입, 로그인, 페이지 권한 관리)
app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["Auth"]
)
app.include_router(fastapi_users.get_register_router(), prefix="/auth", tags=["Auth"])
app.include_router(
    fastapi_users.get_reset_password_router(), prefix="/auth", tags=["Auth"]
)
# 작성한 API include
# app.include_router(userManage.router)
app.include_router(webSocketClient.router)
app.include_router(onestopAnalysis.router)

BASE_DIR=config['dirs']['upload_path']
STT_DIR=config['dirs']['stt_path']

@app.on_event("startup")
async def startup():
    os.makedirs(BASE_DIR, exist_ok=True)
    asyncio.gather(notifier.generator.asend(None))

@app.post("/analysis/whoyouare")
async def judge_who_you_are(file: UploadFile = File(...)):
    '''
    화자 인식 테스트
    '''
    deviceid = file.filename.split('-')[0]
    if "wav" not in file.filename[-3:]:
        raise HTTPException(status_code=422, detail="File extension is not allowed")
    folder = os.path.join(BASE_DIR, deviceid)
    os.makedirs(folder, exist_ok=True)
    soundfile = os.path.join(folder,file.filename)
    with open(soundfile, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    res = voice_recognition(soundfile, ref_voices=[ref_voice_shcho, ref_voice_bsjang], model=models['voice_rec_model'])
    return {"file": file.filename, "result": res}

@app.post("/analysis/stt/wavfile")
async def stt_anal(file: UploadFile = File(...)):
    '''
    wav 파일 업로드 기반 STT
    '''
    if "wav" not in file.filename[-3:]:
        raise HTTPException(status_code=422, detail="File extension is not allowed")
    folder = os.path.join(BASE_DIR, 'stt')
    soundfile = os.path.join(folder,file.filename)
    with open(soundfile, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    res = stt(soundfile, stt_processors, models['stt_model'])
    res = filter_forbidden(res)
    return {"file": file.filename, "result": res}

@app.post("/analysis/id-and-stt")
async def id_and_stt_anal(datatype = 'wavfile', file: UploadFile = File(...)):
    '''
    화자 인식 + STT 테스트
    '''
    deviceid = file.filename.split('-')[0]
    if "wav" not in file.filename[-3:]:
        raise HTTPException(status_code=422, detail="File extension is not allowed")
    folder = os.path.join(BASE_DIR, deviceid)
    os.makedirs(folder, exist_ok=True)
    soundfile = os.path.join(folder,file.filename)
    with open(soundfile, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    speaker = voice_recognition(soundfile, ref_voices=[ref_voice_shcho, ref_voice_bsjang], model=models['voice_rec_model'])
    if speaker == 0:
        speaker = "성훈"
    elif speaker == -1:
        speaker = "??"
    res = stt(soundfile, datatype, stt_processors, models['stt_model'])
    return {"file": file.filename, "result": res, "speaker": speaker}

# WebSocket 연결을 위한 라우트 추가
@app.websocket("/ws/byte")
async def websocket_endpoint2(websocket: WebSocket):
    '''
    녹음된 음원 byte 전송 기반 STT 기본 모델 테스트
    '''
    await notifier.connect(websocket)
    count = 0
    try:
        while True:
            data = await websocket.receive_bytes()
            soundfile = os.path.join(STT_DIR, f'{count}.wav')
            with open(soundfile, "wb") as buffer:
                buffer.write(data)
            res = stt(soundfile, 'wav', stt_processors, models['stt_model'])
            res = filter_forbidden(res)
            response_data = {"data": res}  # 응답할 데이터를 딕셔너리 형태로 구성
            await websocket.send_json(response_data)  # JSON 응답 전송
            # await notifier.push(response_data)
            if count < 20:
                count += 1
            else:
                count = 0
    except WebSocketDisconnect:
        notifier.remove(websocket)

@app.get("/")
async def main():
    content = """
    <body>
    <form action="/upload/" enctype="multipart/form-data" method="post">
    <input name="files" type="file" multiple>
    <input type="submit">
    </form>
    </body>
    """
    return HTMLResponse(content=content)

@app.delete('/files/delete')
async def delete_file(recKey: str):
        target_dir = f'{BASE_DIR}/{recKey[:-2]}/{recKey}'
        target_parent_dir = f'{BASE_DIR}/{recKey[:-2]}'
        print(f'File Delete: {target_dir}')
        if not os.path.exists(target_dir):
            raise HTTPException(status_code=404, detail="No files found")
        delete_result = SoundData().delete(recKey)
        print(f'result:{delete_result}')
        if delete_result:
            shutil.rmtree(target_dir)
            # 상위 디렉토리의 하위 항목 개수 확인
            if len(os.listdir(target_parent_dir)) == 0:  # 하위 폴더가 하나도 없을 경우
                shutil.rmtree(target_parent_dir)  # 상위 디렉토리 삭제
                print(f'Parent Directory Delete: {target_parent_dir}')
            return {"detail": f"Successfully deleted files both from database and server."}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete file from database.")

if __name__ == '__main__':
    uvicorn.run("app:app", host=config['host']['url'], port=int(config['host']['port']), reload=True, 
                reload_excludes=[
                    './logs/*',
                    './pretrained_models/*',
                    './sounds/*',
                    './uploaded_files/*'], 
                log_config=app_log_conf, log_level='info')
