import random
import logging
import schedule


from datetime import date
from sqlalchemy.orm import Session
from asgiref.sync import sync_to_async

from dataBase.models import engine
from dataBase.models import User, University, Admins

# logging.basicConfig(level=logging.ERROR, 
#                     filename='utils/db_errors.log', 
#                     filemode='w',
#                     format="%(asctime)s %(levelname)s %(message)s"
#                     )


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
                registration_date=date.today(),
                )
            session.add(new_user)
            session.commit()
            return 1
    except Exception as e:
        logging.error(f'Ошибка при создании анкеты у пользователя {user_id}', exc_info=True)
        return 0
    
@sync_to_async
def delete_profile(user_id):
    with Session(autoflush=False, bind=engine) as session:
        try:
            obj = session.query(User).filter(User.user_id == user_id).delete()
            session.commit()
            return 1
        except Exception as e:
            return 0

@sync_to_async
def update_active_to_true(user_id):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(User).filter(User.user_id == user_id).first()
        obj.is_active = True
        session.commit()
        return 1
    
@sync_to_async
def update_active_to_false(user_id):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(User).filter(User.user_id == user_id).first()
        obj.is_active = False
        session.commit()
        return 1

@sync_to_async
def update_filter_age_min(user_id, age):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(User).filter(User.user_id == user_id).first()
        obj.min_age = age
        session.commit()
        return 1

@sync_to_async
def update_filter_age_max(user_id, age):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(User).filter(User.user_id == user_id).first()
        obj.max_age = age
        session.commit()
        return 1
    

async def update_filter_university_db(user_id, university):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(User).filter(User.user_id == user_id).first()
        if university == 'all':
            obj.to_university = 3
            session.commit()
            return 1
        else:
            university_id = await get_university_id_by_name(university)
            obj.to_university = university_id
            session.commit()
            return 1

@sync_to_async
def update_filter_cource(user_id, to_cource):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(User).filter(User.user_id == user_id).first()
        obj.to_course = to_cource
        session.commit()
        return 1

@sync_to_async
def update_filter_education_db(user_id, to_education):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(User).filter(User.user_id == user_id).first()
        obj.to_education = to_education
        session.commit()
        return 1




@sync_to_async
def get_list_of_profiles(
    user_id,
    to_education,
    to_university,
    to_course,
    max_age,
    min_age
    ):
    try:
        with Session(autoflush=False, bind=engine) as session:
            obj = session.query(User).filter(User.user_id == user_id).first()
            list_of_profiles = []
            whom = obj.search_to
            users = session.query(User).filter(User.is_active == True).filter(User.is_blocked == False).filter(User.user_id != user_id)
            if to_education != 'all':
                users = users.filter(User.education == to_education)
            if to_university != 3:
                users = users.filter(User.university == to_university)
            if to_course != 0:
                users = users.filter(User.course == to_course)
            if max_age != 0:
                users = users.filter(User.age <= max_age)
            if min_age != 0:
                users = users.filter(User.age >= min_age)
            users = users.all()
            if users is not None:
                
                for user in users:
                    if user.sex == whom:
                        list_of_profiles.append(user.user_id)
                
                if len(list_of_profiles) == 1:
                    return list_of_profiles
                elif len(list_of_profiles) == 0:
                    return []
                elif len(list_of_profiles) > 1:
                    
                    random.shuffle(list_of_profiles)
                    return list_of_profiles
            else:
                return list_of_profiles
    except Exception as e:
        logging.error(f'Ошибка при создании списка подбираемых анкет у пользователя {user_id}', exc_info=True)

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
    if obj.name == 'all':
        return 'Все'
    else:
        return obj.name


@sync_to_async
def change_description_by_id(user_id, text):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(User).filter(User.user_id==user_id).first()
        obj.description = text
        session.commit()
        return 1

@sync_to_async
def change_age_by_id(user_id: str, age: int):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(User).filter(User.user_id == user_id).first()
        obj.age = age
        session.commit()
        return 1

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
                    "user_name": obj.user_name,
                    "to_university": obj.to_university,
                    "to_education": obj.to_education,
                    "to_course": obj.to_course,
                    "max_age": obj.max_age,
                    "min_age": obj.min_age,
                    "is_blocked": obj.is_blocked,
                    "is_active": obj.is_active,
                    "user_id": obj.user_id,
                    "search_to": obj.search_to,
                }
                match data["education"]:
                    case 'spo':
                        data["education"] = 'СПО'
                    case 'bakalavriat':
                        data["education"] = 'Бакалавриат'
                    case 'specialitet':
                        data["education"] = 'Специалитет'
                    case 'magistratura':
                        data["education"] = 'Магистратура'
                if not Anketa:
                    return data
                elif Anketa:
                    university = await get_university_name_by_id(data["university"])
                    return f'\
{data["name"]}, \
{data["age"]}, \
{university} - {data["speciality"]}\
({data["course"]} курс, \
{data["education"]})\n\n\
{data["description"]}'
            except Exception as e:
                logging.error(f'Ошибка при получении анкеты пользователя с парраметром Anketa = {Anketa}, user_id = {user_id}')
                return 'Error'
        else:
            return 'User not found'

        





############### admin ###############
        
@sync_to_async
def get_list_of_admins():
    with Session(autoflush=False, bind=engine) as session:
        list_of_admins = []
        admins = session.query(Admins).all()
        for admin in admins:
            list_of_admins.append(admin.user_id)
        return list_of_admins
            

@sync_to_async
def block_user_db(user_id):
    try:
        with Session(autoflush=False, bind=engine) as session:
            obj = session.query(User).filter(User.user_id == user_id).first()
            obj.is_blocked = True
            session.commit()
            return 1
    except Exception as e:
        return 0
    
@sync_to_async
def unblock_user_db(user_id):
    try:
        with Session(autoflush=False, bind=engine) as session:
            obj = session.query(User).filter(User.user_id == user_id).first()
            obj.is_blocked = False
            session.commit()
            return 1
    except Exception as e:
        return 0

@sync_to_async
def get_statistic_user_db():
    with Session(autoflush=False, bind=engine) as session:
        users = session.query(User).all()
        count_active = session.query(User).filter(User.is_active == True).filter(User.is_blocked == False).all()
    return len(users), len(count_active)
        

@sync_to_async
def get_list_of_users_for_spam_db(is_admin_search=False):
    with Session(autoflush=False, bind=engine) as session:
        users = []
        if not is_admin_search:
            objs = session.query(User).filter(User.is_active == True).filter(User.is_blocked == False).all()
        else:
            objs = session.query(User).all()
        for user in objs:
            users.append(user.user_id)
    return users


@sync_to_async
def add_admin_db(user_id):
    with Session(autoflush=False, bind=engine) as session:
        new_admin = Admins(user_id=user_id)
        session.add(new_admin)
        session.commit()
        return 1
    

@sync_to_async
def delete_admin_db(user_id):
    with Session(autoflush=False, bind=engine) as session:
        session.query(Admins).filter(Admins.user_id == user_id).delete()
        session.commit()
        return 1
    
@sync_to_async
def add_university_db(name):
    try:
        with Session(autoflush=False, bind=engine) as session:
            new_university = University(name=name)
            session.add(new_university)
            session.commit()
            return 1
    except Exception as e:
        logging.error('Ошибка при добавлении университета', exc_info=True)
        return 0
    
@sync_to_async
def delete_university_db(name):
    try:
        with Session(autoflush=False, bind=engine) as session:
            session.query(University).filter(University.name == name).delete()
            session.commit()
            return 1
    except Exception as e:
        logging.error('Ошибка при удалении университета', exc_info=True)
        return 0