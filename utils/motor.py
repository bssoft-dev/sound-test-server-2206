import json
from motor.motor_tornado import MotorCollection
from fastapi import HTTPException
from typing import List

async def count(table: MotorCollection, check: json) -> int:
    try:
        res = table.count_documents(check)
        return await res
    except Exception as e:
        raise HTTPException(status_code=505, detail=str(e))


async def select_one(table: MotorCollection, check: json) -> json:
    try:
        res = table.find_one(check)
        return await res
    except Exception as e:
        raise HTTPException(status_code=505, detail=str(e))


async def select_many(table: MotorCollection, check: json, limit = None) -> List:
    try:
        res = table.find(check)
        return await res.to_list(length=limit)
    except Exception as e:
        raise HTTPException(status_code=505, detail=str(e))


async def select_and_sort(table: MotorCollection, check: json, sort: str, sortType: str = 'desc', limit = 100) -> List:
    try:
        if sortType == 'desc':
            res = table.find(check).sort(sort, -1)
        else:
            res = table.find(check).sort(sort, 1)
        return await res.to_list(length=limit)
    except Exception as e:
        raise HTTPException(status_code=505, detail=str(e))


async def insert_one(table: MotorCollection, data: json):
    try:
        res = table.insert_one(data)
        return await res
    except Exception as e:
        raise HTTPException(status_code=505, detail=str(e))


async def insert_many(table: MotorCollection, data: List):
    try:
        res = table.insert_many(data)
        return await res
    except Exception as e:
        raise HTTPException(status_code=505, detail=str(e))


async def update_one(table: MotorCollection, check: json, data: json):
    try:
        res = await table.update_one(check, {'$set':data})
        return res
    except Exception as e:
        raise HTTPException(status_code=505, detail=str(e))

async def pull_update(table: MotorCollection, check: json, pull_data: json):
    try:
        res = await table.update_many(check, {'$pull': pull_data})
        return res
    except Exception as e:
        raise HTTPException(status_code=505, detail=str(e))

async def delete_one(table: MotorCollection, check: json):
    try:
        res = await table.delete_one(check)
        return res
    except Exception as e:
        raise HTTPException(status_code=505, detail=str(e))


async def delete_many(table: MotorCollection, check: json):
    try:
        res = await table.delete_many(check)
        return res
    except Exception as e:
        raise HTTPException(status_code=505, detail=str(e))

# Bulk transaction for same table
async def bulk_write(table: MotorCollection, data: List):
    try:
        res = await table.bulk_write(data)
        return res
    except Exception as e:
        raise HTTPException(status_code=505, detail=str(e))