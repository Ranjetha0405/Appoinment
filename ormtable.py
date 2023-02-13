from sqlalchemy import Integer,Column, String,BigInteger,ForeignKey, DateTime, Date, Time,TIMESTAMP, text, UniqueConstraint
from database import Base

class Id():
    id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)

class User(Id,Base):
    __tablename__ = "user"
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    mobile = Column(BigInteger, nullable=False, index=True, unique=True)
    email = Column(String(100), nullable = False)
    user_timezone = Column(TIMESTAMP, nullable = False, server_default=text("CURRENT_TIMESTAMP"))

class Client(Id,Base):
    __tablename__ = "client"
    client_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable = False, index=True, unique=True)
    password = Column(String(250), nullable = False)
    location = Column(String(25), nullable = False)
    timezone = Column(TIMESTAMP, nullable = False, server_default=text("CURRENT_TIMESTAMP"))

class ClientAvailable(Id,Base):
    __tablename__ = "client_available"
    client_id = Column(Integer, ForeignKey(column = 'client.id'), nullable=False)
    available_date = Column(Date, nullable = False)
    # available_enddate = Column(Date, nullable = False)
    available_starttime = Column(Time, nullable = True)
    available_endtime = Column(Time, nullable = True)
    UniqueConstraint(client_id, available_date,available_starttime, name='client_availability_starttime')
    UniqueConstraint(client_id, available_date,available_endtime, name='client_availability_endtime')

class Appoinment(Id,Base):
    __tablename__ = "appoinment"
    user_id = Column(Integer, ForeignKey(column ='user.id'), nullable=False)
    client_id = Column(Integer, ForeignKey(column ='client.id'), nullable=False)
    Appoinment_purpose = Column(String(250), nullable = False)
    Appoinment_date = Column(Date, nullable=False)
    Appoinment_time = Column(Time, nullable= False)
    created_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    modified_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    duration = Column(Time, nullable= False)
    UniqueConstraint(client_id, user_id, Appoinment_date,Appoinment_time, name='appoinment_booking')