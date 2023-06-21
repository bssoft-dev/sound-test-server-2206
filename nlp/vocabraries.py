forbidden_sentences = [
    ' MBC 뉴스 김수근입니다.', 
    ' 안녕히계세요.', 
    ' 아', 
    ' 감사합니다.', 
    ' 잘자요', 
    ' 끝', 
    ' 잘 먹었습니다.',
    ' 고추장',
    ' 된장',
    ' 고춧가루',
    ' 이 노래는 제가 좋아하는 노래입니다.',
    ' 안녕',
    ' 이 시각 세계였습니다.',
    ' 다음 영상에서 만나요!',
    ' 자, 그럼 다음 영상에서 만나요!',
    ' 이 영상은 유료 광고를 포함하고 있습니다.',
    ' 박수',
    ' 잘자요',
    ' 잘 들었습니다.',
    ' 이제는 마트에 가서 먹으러 갈게요'
    ]

forbidden_starts = [' 아 아 아 아 아 아 아 아', ' 마이크가 너무 작아서,']

def filter_forbidden(text: str):
    if text.startswith(forbidden_starts[0]) or text.startswith(forbidden_starts[1]):
        return ''
    elif text in forbidden_sentences:
        return ''
    else:
        return text