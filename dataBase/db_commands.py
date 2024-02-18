from dataBase.models import engine
from dataBase.models import User, University

from datetime import date
from sqlalchemy.orm import Session
from asgiref.sync import sync_to_async

@sync_to_async
def create_user(
    name, 
    sex, 
    age, 
    user_name, 
    user_id,
    photos, 
    university,
    speciality, 
    course, 
    education, 
    description=''
    ):

    with Session(autoflush=False, bind=engine) as session:
        new_user = User(
            name=name, 
            sex=sex, 
            age=age, 
            description=description,
            user_name=user_name, 
            user_id=user_id, 
            is_active=True,
            photos=photos, 
            university=university,
            speciality=speciality, 
            course=course, 
            education=education, 
            is_blocked=False,
            registration_date=date.today()
            )
        session.add(new_user)
        session.commit()



@sync_to_async
def has_register(user_id):
    with Session(autoflush=False, bind=engine) as session:
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            name = user.name
            return 1
        except:
            return 0
        
@sync_to_async
def read_university():
    with Session(autoflush=False, bind=engine) as session:
        rezult = []
        universitis = session.query(University).all()
        for i in universitis:
            rezult.append(i.name)
    return rezult

@sync_to_async
def get_university_id_by_name(university):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(University).filter(University.name==university).first()
    return obj.id

@sync_to_async
def get_university_name_by_id(un_id):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(University).filter(University.id==un_id).first()
    return obj.name


        



        

    