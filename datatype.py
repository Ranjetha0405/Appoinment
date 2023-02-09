from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime

class Id(BaseModel):
    id : Optional[int]

class ClientId(BaseModel):
     client_id : int

class UserDetails(Id,BaseModel):
    first_name : str 
    last_name : str  
    mobile : int  
    user_timezone : Optional[datetime]
    email : str 

class ClientDetails(Id,BaseModel):
    client_name : str 
    email : str 
    password : str 
    location : str 
    timezone : Optional[datetime]
   
class ClientAvailable(Id, ClientId,BaseModel):
    available_date : date
    # available_enddate : date
    available_starttime : Optional[time]
    available_endtime : Optional[time]
"""
class ClientUnAvailable(Id,ClientId,BaseModel):
    unavailable_date : date
    unavailable_starttime : time
    unavailable_endtime : time

"""
class AppoinmentCreateDetails(ClientId,BaseModel):
    user_id : int
    Appoinment_date : date
    Appoinment_time : time
    duration : time
    Appoinment_purpose :str

class SendEmail(BaseModel):
    email_to: str
    subject : str


class AppoinmentDetails(Id,ClientId,BaseModel):
    user_id : int
    Appoinment_date : date
    Appoinment_time : time
    duration : time
    created_date: Optional[date]
    modified_date: Optional[date]
    Appoinment_purpose :str

