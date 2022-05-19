# sound-test-server-2206
사운드 테스트를 위한 서버(BE)입니다.  
[swagger페이지 링크](http://sound.bs-soft.co.kr/docs)

## requirements  
`dockerfile`과 `requirements.txt`에 모두 표기

## 실행방법  

1. 저장소 복제
~~~bash
git clone https://github.com/bssoft-dev/sound-test-server-2206.git  
~~~  
2. (옵션1) GPU를 사용하는 경우 - gpus 옵션을 주고 실행(`all` 또는 `device=0`등)
~~~bash
docker run --gpus all -d -v $(pwd)/sound-test-server-2206:/bssoft --network=host bssoftdev/bssoft-sound-process
~~~  
3. (옵션2) GPU를 사용하지 않는 경우 - config를 cpu로 변경하고 실행
~~~bash
vi sound-test-server-2206/config.ini
# device = gpu 부분을 cpu로 변경 및 저장한다
docker run -d -v $(pwd)/sound-test-server-2206:/bssoft --network=host bssoftdev/bssoft-sound-process
~~~

## config.ini 설명
`[host]` 서버 실행 url과 port 설정  
`[dirs]` 파일 업로드, 로그, 임시 파일, 타겟 파일 위치 설정  
`[ml]` device: `cpu` 혹은 `gpu`, model: 사용 모델 위치  
`[tcp]` tcp 소켓 통신을 위함(utils/processor.py) 현재는 사용하지 않음
[bss 테스트 서버](https://github.com/bssoft-dev/bss-api-2206)와 비슷한 역할을 합니다.  
audio 파일을 업로드 하였을 때 처리상태를 확인하고 다운받을 수 있습니다.  
