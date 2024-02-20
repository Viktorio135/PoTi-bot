import random

from dataBase.models import engine
from dataBase.models import User, University

from datetime import date
from sqlalchemy.orm import Session
from asgiref.sync import sync_to_async

@sync_to_async
def create_user(
    name, 
    sex, 
    search_to,
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
    try:
        with Session(autoflush=False, bind=engine) as session:
            new_user = User(
                name=name, 
                sex=sex, 
                search_to=search_to,
                age=age, 
                description=description,
                user_name=user_name, 
                user_id=user_id, 
                is_active=False,
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
            return 1
    except:
        return 0
    
@sync_to_async
def delete_profile(user_id):
    with Session(autoflush=False, bind=engine) as session:
        try:
            obj = session.query(User).filter(User.user_id == user_id).delete()
            session.commit()
            return 1
        except Exception as e:
            print(e)
            return 0

@sync_to_async
def update_active(user_id):
    try:
        with Session(autoflush=False, bind=engine) as session:
            obj = session.query(User).filter(User.user_id == user_id).update({User.is_active: True})
        return 1
    except:
        return 0

@sync_to_async
def get_list_of_profiles(user_id):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(User).filter(User.user_id == user_id).first()
        list_of_profiles = []
        whom = obj.search_to
        users = session.query(User).all()
        if users != None:
            
            for user in users:
                if user.sex == whom:
                    list_of_profiles.append(user.user_id)
            
            if len(list_of_profiles) == 1:
                return list_of_profiles
            elif len(list_of_profiles) == 0:
                return []
            elif len(list_of_profiles) > 1:
                
                random.shuffle(list_of_profiles)
                print(list_of_profiles)
                return list_of_profiles
        else:
            return list_of_profiles

        


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


async def get_user_by_id(user_id, Anketa=False):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(User).filter(User.user_id == user_id).first()
        
        if obj is not None:
        
            try:
                data = {
                    "name": obj.name,
                    "sex": obj.sex,
                    "age": obj.age,
                    "description": obj.description,
                    "photos": obj.photos,
                    "university": obj.university,
                    "speciality": obj.speciality,
                    "course": obj.course,
                    "education": obj.education,
                    "user_name": obj.user_name
                }
                if not Anketa:
                    return data
                elif Anketa:
                    university = await get_university_name_by_id(data["university"])
                    return f'{data["name"]}, {data["age"]}, {university} - {data["speciality"]}({data["course"]} курс, {data["education"]})\n\n{data["description"]}'
            except Exception as e:
                print(e)
                return 'Error'
        else:
            return 'User not found'

        



        

    