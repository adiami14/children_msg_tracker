import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from api_database import MySQLServer, DB_CONFIG

db_server = MySQLServer(DB_CONFIG)
db_server.connect()

# Define request models
class InsertRequest(BaseModel):
    table_name: str
    data: dict

class UpdateRequest(BaseModel):
    table_name: str
    data: dict
    where_clause: str

class DeleteRequest(BaseModel):
    table_name: str
    where_clause: str

@app.get("/data/{table_name}")
async def do_get(table_name: str):
    try:
        data = db_server.get_data(table_name)
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/data/insert")
async def do_post_insert(request: InsertRequest):
    try:
        last_id = db_server.insert_data(request.table_name, request.data)
        return {"status": "success", "inserted_id": last_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/data/update")
async def do_post_update(request: UpdateRequest):
    try:
        updated_rows = db_server.update_data(request.table_name, request.data, request.where_clause)
        return {"status": "success", "updated_rows": updated_rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/data/delete")
async def do_post_delete(request: DeleteRequest):
    try:
        deleted_rows = db_server.delete_data(request.table_name, request.where_clause)
        return {"status": "success", "deleted_rows": deleted_rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
