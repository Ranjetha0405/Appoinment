from fastapi import APIRouter
from custom_classes import APIRouteWrapper, CustomRequest
import ormtable, utils
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from database import get_db
from fastapi import APIRouter, Depends
import json
from sqlalchemy.orm import Session
from datatype import ClientDetails
from authentication import create_access_token
from fastapi.responses import JSONResponse
from datatype import ClientAvailable
from sqlalchemy import and_

router = APIRouter(route_class=APIRouteWrapper)


@router.post("/client/updatedata/login", tags=["client"])
def add_client(login: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    data_in_db = db.query(ormtable.Client).filter(ormtable.Client.email == login.username).first()
    if data_in_db :
        if not utils.verify(login.password, data_in_db.password):
            return JSONResponse({"data": [], "status": "error","message": "Incorrect password"})
        else:
            client_dict = ClientDetails.parse_obj(data_in_db.__dict__).dict(exclude={"password"})
            access_token = create_access_token(data={"client_id": data_in_db.id})
            return JSONResponse(json.loads(json.dumps({"data": {**client_dict, "access_token": access_token, "token_type": "bearer" },"status":"success", "message": "login successful"}, default=str)))
            # return JSONResponse(json.loads(json.dumps({'data':client_dict, 'message': 'Login Successful', "status": "success"},default=str)))
    else:
        return JSONResponse({'data':[], 'message': 'email_id doesnot exist', "status": "success"})

@router.post("/client/availabledata", tags=["client"])
def add_client_availability(payload: ClientAvailable , request: CustomRequest, db: Session = Depends(get_db)):
    new_post = ormtable.ClientAvailable(**payload.dict())
    new_data = ClientAvailable(**new_post.__dict__).dict()
    client_id = request.logged_in_user_id
    client_id_user = new_data.get("client_id")
    ava_date = new_data.get("available_date")
    ava_start_time = new_data.get("available_starttime")
    ava_end_time = new_data.get("available_endtime")

    #SQL Query --> SELECT available_starttime FROM `client_available` WHERE client_id = 1 and available_starttime BETWEEN '09:00:00' AND '14:00:00';

    if client_id_user == client_id:
        data_in_db = db.query(ormtable.ClientAvailable.available_starttime, ormtable.ClientAvailable.available_date).filter(ormtable.ClientAvailable.client_id == client_id,ormtable.ClientAvailable.available_date == ava_date, and_(ormtable.ClientAvailable.available_starttime >= ava_start_time, ormtable.ClientAvailable.available_starttime <= ava_end_time)).all() 
        print(data_in_db)
        if data_in_db == []:
            db.add(new_post)
            db.commit()
            db.refresh(new_post)
            return JSONResponse({'data':[ClientAvailable.parse_obj(new_post.__dict__).dict()], 'message': 'added successfully', "status": "success"})
        else:
            return JSONResponse({'data':[], 'message': 'client already engaged in that time', "status": "success"})
    else:
        return JSONResponse({'data':[], 'message': 'client Id doesnt match', "status": "success"})


