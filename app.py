from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from database import get_db, Base, engine
from sqlalchemy.orm import Session
from sqlalchemy import func
import uvicorn, ormtable, utils, login
from datatype import ClientDetails, UserDetails, AppoinmentDetails, AppoinmentCreateDetails, SendEmail
import json, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

tags_metadata = [
    {
        "name": "user",
        "description": "User details.",
    },
    {
        "name": "client",
        "description": "Client details.",
    },
    {
        "name": "appoinment",
        "description": "Appoinment details.",
    },
]

app = FastAPI(openapi_tags=tags_metadata)

app.include_router(login.router)

Base.metadata.create_all(bind=engine)

@app.get("/user/details", tags=["user"])
def user(db: Session = Depends(get_db)):
    posts = db.query(ormtable.User).all()
    if not posts:
        return JSONResponse({"data": [],
                             "status": "success",
                             "message": "No user found"})
    return JSONResponse(json.loads(json.dumps({"data": [UserDetails.parse_obj(post.__dict__).dict() for post in posts],
                         "status": "success",
                         "message": "success"},default=str)))

@app.get("/client/details", tags=["client"])
def client(db: Session = Depends(get_db)):
    posts = db.query(ormtable.Client).all()
    if not posts:
        return JSONResponse({"data": [],
                             "status": "success",
                             "message": "No client found"})
    return JSONResponse(json.loads(json.dumps({"data": [ClientDetails.parse_obj(post.__dict__).dict(exclude={"password"}) for post in posts],
                         "status": "success",
                         "message": "success"},default=str)))

@app.get("/appoinment/details", tags=["appoinment"])
def appoinment(db: Session = Depends(get_db)):
    posts = db.query(ormtable.Appoinment).all()
    if not posts:
        return JSONResponse({"data": [],
                             "status": "success",
                             "message": "No appoinment found"})
    return JSONResponse(json.loads(json.dumps({"data": [AppoinmentDetails.parse_obj(post.__dict__).dict() for post in posts],
                         "status": "success",
                         "message": "success"},default=str)))


@app.post("/user/updatedata", tags=["user"])
def add_user(payload: UserDetails ,db: Session = Depends(get_db)):
    new_post = ormtable.User(**payload.dict())
    new_data = UserDetails(**new_post.__dict__).dict()
    mobile = new_data.get("mobile")
    data_in_db = db.query(ormtable.User.mobile).filter(ormtable.User.mobile == mobile).all()
    if data_in_db == []:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return JSONResponse(json.loads(json.dumps({'data':[UserDetails.parse_obj(new_post.__dict__).dict()], 'message': 'added successfully', "status": "success"},default=str)))
    else:
        return JSONResponse({'data':[], 'message': 'Mobile number already exists', "status": "success"})


@app.post("/client/updatedata/signup", tags=["client"])
def add_client(payload:ClientDetails ,db: Session = Depends(get_db)):
    payload.password= utils.hash(payload.password)
    new_post = ormtable.Client(**payload.dict())
    new_data = ClientDetails(**new_post.__dict__).dict()
    email = new_data.get("email")
    data_in_db = db.query(ormtable.Client.email).filter(ormtable.Client.email == email).all()
    if data_in_db == []:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return JSONResponse(json.loads(json.dumps({'data':[ClientDetails.parse_obj(new_post.__dict__).dict(exclude={"password"})], 'message': 'added successfully', "status": "success"},default=str))) 
    else:
        return JSONResponse({'data':[], 'message': 'email_id already exists', "status": "success"})


@app.post("/appoinment/createdata", tags=["appoinment"])
def add_appoinment(background_tasks: BackgroundTasks, payload: AppoinmentCreateDetails ,db: Session = Depends(get_db)):
    # payload_data = json.loads(json.dumps(payload,default=str))
    # print(payload_data)
    new_post = ormtable.Appoinment(**payload.dict())
    new_data = AppoinmentDetails(**new_post.__dict__).dict()
    user_id = new_data.get("user_id")  
    client_id = new_data.get("client_id")
    Appoinment_date = new_data.get("Appoinment_date")
    Appoinment_time = new_data.get("Appoinment_time")
    availability = db.query(ormtable.ClientAvailable.available_date, func.group_concat(ormtable.ClientAvailable.available_starttime ,'|', ormtable.ClientAvailable.available_endtime ).label("available_time_slots")).filter(ormtable.ClientAvailable.client_id == client_id,ormtable.ClientAvailable.available_date == Appoinment_date).group_by(ormtable.ClientAvailable.available_date).all() 
    if availability:
        available_time = availability[0][1]
        if available_time == None:
            return JSONResponse({'data': [], 'message': 'client is not available on the given date', "status": "success"})    
        seperate_time = available_time.split(',')
        for single_time in seperate_time:
            time = single_time.split('|')
            from_time = time[0]
            to_time = time[1]
            if from_time <= Appoinment_time.strftime("%H:%M:%S")  <= to_time :
                db.add(new_post)
                db.commit()
                db.refresh(new_post)
                
                user_mail_data = db.query(ormtable.User.email, ormtable.User.first_name, ormtable.User.last_name).filter(ormtable.User.id == user_id).first()
                client_mail_data = db.query(ormtable.Client.email, ormtable.Client.client_name).filter(ormtable.Client.id == client_id).first()
                
                payload_user = """\
                                    <html>
                                    <body>
                                        <p><h2> Hi """ +user_mail_data[1]+' '+user_mail_data[2]+""",</h2><br>
                                        <h3> <b>You booked an appoinment</b> <br>
                                        Name : """+client_mail_data[1]+"""<br>
                                        On date : """ +str(payload.Appoinment_date)+ """<br>
                                        From time : """ +str(payload.Appoinment_time)+""" <br>
                                        Duration: """+ str(payload.duration)+"""<br>
                                        Purpose : """ +str(payload.Appoinment_purpose)+""" <b>is confirmed </b></h3><br><br>
                                        <h3>Thank You</h3><br>
                                        </p>
                                    </body>
                                    </html>
                                    """
                payload_client = """\
                                        <html>
                                        <body>
                                            <p><h2> Hi """ + client_mail_data[1] + """,</h2><br>
                                            <h3><b> You are booked by </b><br>
                                            Name : """ +user_mail_data[1] +' ' +user_mail_data[2]+ """<br>
                                            On date : """ +str(payload.Appoinment_date)+ """<br>
                                            From time : """ +str(payload.Appoinment_time)+""" <br>
                                            Duration: """+ str(payload.duration)+"""<br>
                                            Purpose : """ +str(payload.Appoinment_purpose)+""" <b>is confirmed </b></h3><br><br>
                                            <h3>Thank You</h3><br>
                                            </p>
                                        </body>
                                        </html>
                                        """

                background_tasks.add_task(mail, user_mail_data[0], "appoinment confirmation details", payload_user)
                background_tasks.add_task(mail, client_mail_data[0], "appoinment confirmation details" , payload_client)
                return JSONResponse({'data':[AppoinmentDetails.parse_obj(new_post.__dict__).dict()], 'message': 'Appoinment marked and email sent', "status": "success"})
        return JSONResponse({'data':[], 'message': 'client not available on given time', "status": "success"})
    else:
        return JSONResponse({'data': [], 'message': 'client out of station', "status": "success"})


@app.get("/client-availability-time-to-user/{client_id}", tags=["user"])
def check_client_availability(client_id : int, db: Session = Depends(get_db)):
    availability = db.query(ormtable.ClientAvailable.available_date, func.group_concat(ormtable.ClientAvailable.available_starttime ,'|', ormtable.ClientAvailable.available_endtime ).label("available_time_slots")).filter(ormtable.ClientAvailable.client_id == client_id).group_by(ormtable.ClientAvailable.available_date).all() 
    if availability:
        available =[]
        for ava in availability:
            available_dates = ava[0]
            available_time = ava[1]
            if available_time == None:
                available.append({"date": available_dates, "status" : "unavailable" , "time":{}})
            else:
                available_start = []
                seperate = available_time.split(',')
                for single_time in seperate:
                    time = single_time.split('|')
                    from_time = time[0]
                    to_time = time[1]
                    available_start.append({"from" : from_time, "to" : to_time })
                    appoinment = db.query(ormtable.Appoinment.Appoinment_time,ormtable.Appoinment.duration).filter(ormtable.Appoinment.client_id == client_id, ormtable.Appoinment.Appoinment_date == available_dates).all()
                    booked = []
                    for app in appoinment:
                        unava_from_time = app[0]
                        unava_to_time = app[1]
                        booked.append({"from" : unava_from_time, "duration" : unava_to_time })
                available.append({"date": available_dates, "status" : "available" , "time":{"available" : available_start, "booked" : booked}})
        return JSONResponse(json.loads(json.dumps({'data': available, "message": "client exists", "status": "success"},default=str)))  
    else:
        return JSONResponse({'data': [], 'message': 'client doesnot exists', "status": "success"})


def mail(to, subject, text):

    if not isinstance(to, list):
        to = [to]

    gmail_user='ranjetha0405@gmail.com'
    gmail_pwd = "pimhsnupnpvnmbuz"
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = ", ".join(to)
    msg['Subject'] = subject

    msg.attach(MIMEText(text,"html"))

    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmail_user, gmail_pwd)
    mailServer.sendmail(gmail_user, to, msg.as_string())
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()

if __name__ == '__main__':
    uvicorn.run(app=app, port=8000)


