import aiohttp
import json
import time
import hashlib
import hmac
import base64


async def sms_send(sendSmsList, content):
    service_id = 'ncp:sms:kr:283078791279:smartbell'
    # service_id = 'ncp:sms:kr:281232554365:test'
    url = "https://sens.apigw.ntruss.com"
    uri = "/sms/v2/services/" + service_id + "/messages"
    api_url = url + uri
    timestamp = str(int(time.time() * 1000))
    access_key = 'iHAGxSJm4sReuTo6leRO' # 실제 계정의 엑세스키
    # access_key = 'cID301sx8FbehX0A3mTZ' # 실제 계정의 엑세스키
    string_to_sign = "POST " + uri + "\n" + timestamp + "\n" + access_key
    signature = make_signature(string_to_sign)

    headers = {
        'Content-Type': "application/json; charset=UTF-8",
        'x-ncp-apigw-timestamp': timestamp,
        'x-ncp-iam-access-key': access_key,
        'x-ncp-apigw-signature-v2': signature
    }

    body = {
        "type": "SMS",
        "contentType": "COMM",
        "from": "01022498703",
        "content": content,
        "countryCode": "82"
    }
    body['messages'] = []
    # 전화번호 목록에 대해 일괄전송
    for phoneNumber in sendSmsList:
        body['messages'].append(
            {
            "to": phoneNumber,
            "subject": "지키다 앱 SOS 문자",
            "content": content
            }
        )
    body = json.dumps(body)
    async with aiohttp.ClientSession(headers=headers) as session:
        response = await session.post(api_url, data=body)
        response.raise_for_status()


def make_signature(string):
    secret_key = bytes("3rt127vI8pohVWPe5hyop6sjAZuzRExpxoWQKHRY", 'UTF-8')
    # secret_key = bytes("90sg6Oo1weyNBAXi5qx8jR7TvhJP1JkB7m8BaHX5", 'UTF-8')
    string = bytes(string, 'UTF-8')
    string_hmac = hmac.new(secret_key, string, digestmod=hashlib.sha256).digest()
    string_base64 = base64.b64encode(string_hmac).decode('UTF-8')
    return string_base64