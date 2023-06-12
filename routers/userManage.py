from fastapi import APIRouter, Depends
from models import UserDB, UserUpdate, UserSuperUpdate
# from resp_model import UserAll
# from email.mime.text import MIMEText
# from subprocess import Popen, PIPE
from database import userT
from users import current_super_user, current_hyper_user, current_active_user

from environment import hyper_name

router = APIRouter(tags=['User'])

@router.get("/users/all")
async def get_all_users(username:str, super: UserDB = Depends(current_super_user)):
    """
    사용자 정보 전체 조회
    """
    user_list = []
    try:
        if username == hyper_name:
            async for user in userT.find({'username':{'$nin':[hyper_name]}}):
                # print(user)
                # user_list.append(UserAll(user.dict()))
                user_list.append(user)
        else:
            async for user in userT.find({'username':username, 'username':{'$nin':[hyper_name]}}):
                # print(user)
                # user_list.append(UserAll(user.dict()))
                user_list.append(user)
    except Exception as e: 
        print('user find error : ', e)
    resultSort=sorted(user_list, reverse=True, key=lambda k: k['name'])
    return resultSort

@router.get("/users/{username}")
async def get_one_user(username:str, super: UserDB = Depends(current_super_user)):
    """
    특정 사용자 정보 조회
    """
    try:
        if username == hyper_name: 
            result = await userT.find_one({'username':username},{'_id':0})
        else : 
            result = await userT.find_one({'username':username, 'username':username},{'_id':0})
    except Exception as e: 
        print('user find error : ', e)
    return result

@router.put("/users/{username}")
async def modify_one_user(username: str, user: UserUpdate, super : UserDB = Depends(current_super_user)):
    """
    특정 사용자 정보 수정
    """
    document = user.dict()
    try:
        userId = await userT.find_one({'username':username},{'id':1, '_id':0})
        await userT.update_one({'id':userId['id']},{'$set':document})   
        result = await userT.find_one({'id':userId['id']})
    except Exception as e: 
        print('user modify error : ', e)
    return result

@router.delete("/users/{username}")
async def delete_one_user(username: str, hyper : UserDB = Depends(current_hyper_user)):
    """
    특정 사용자 삭제
    """
    try:
        userId = await userT.find_one({'username':username},{'username':1, '_id':0})
        await userT.delete_one({'username':userId['username']})
        deleteCheck = await userT.find_one({'username':userId['username']})
    except Exception as e: 
        print('user delete error : ', e)
    if deleteCheck is None:
        result = {"result": "delete success"}
    else:
        result = {"result": "delete fail"}
    return result

@router.get("/users/duplicate/{username}")
async def duplicate_check_name_user(username: str):
    """
    특정 사용자의 아이디 중복 확인
    """
    try:
        user = userT.find({},{'_id':0,'username':1})
    except Exception as e: print('user find error : ', e)
    user_list = await user.to_list(length=None)
    for i in range(len(user_list)):
        if user_list[i]['username'] == username: 
            return '중복된 아이디 입니다'
    for i in range(len(user_list)):
        if user_list[i]['username'] != username: 
            return '생성 가능한 아이디 입니다'

@router.put("/users/superGrant/{username}")
async def one_user_super_grant(username: str, user: UserSuperUpdate, super : UserDB = Depends(current_super_user)):
    """
    특정 사용자 슈퍼 권한 부여
    """
    document = user.dict()
    try:
        await userT.update_one({'username':username},{'$set':{'is_superuser':document['is_superuser']}})
        result = await userT.find_one({'username':username})
    except Exception as e: 
        print('user grant error : ', e)
    return result