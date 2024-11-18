import random
import logging
import schedule


from datetime import date
from sqlalchemy.orm import Session
from asgiref.sync import sync_to_async

from dataBase.models import engine
from dataBase.models import User, Admins



@sync_to_async
def create_user(
    name, 
    game_id,
    user_id,
    username,
    screenshot1,
    screenshot2,
    description,
    role1,
    role2,
    role3,
    promocode
    ):
    try:
        with Session(autoflush=False, bind=engine) as session:
            new_user = User(
                name=name, 
                game_id=game_id,
                description=description,
                role1=role1,
                role2=role2,
                role3=role3,
                screenshot1=screenshot1,
                screenshot2=screenshot2,
                user_name=username, 
                user_id=user_id, 
                promocode=promocode,
                is_active=False,
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
def update_screenshots(user_id, screenshot1, screenshot2):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(User).filter(User.user_id == user_id).first()
        obj.screenshot1 = screenshot1
        obj.screenshot2 = screenshot2
        session.commit()
        return 1


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
def get_list_of_profiles(
    user_id
    ):
    try:
        with Session(autoflush=False, bind=engine) as session:
            obj = session.query(User).filter(User.user_id == user_id).first()
            list_of_profiles = []
            users = session.query(User).filter(User.is_active == True).filter(User.is_blocked == False).filter(User.user_id != user_id).all()
            if users is not None:
                for user in users:
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
def change_description_by_id(user_id, text):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(User).filter(User.user_id==user_id).first()
        obj.description = text
        session.commit()
        return 1



async def get_user_by_id(user_id, Anketa=False):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(User).filter(User.user_id == user_id).first()
        if obj is not None:
            try:
                data = {
                    "name": obj.name,
                    "game_id": obj.game_id,
                    "description": obj.description,
                    "role1": obj.role1,
                    "role2": obj.role2,
                    "role3": obj.role3,
                    "screenshot1": obj.screenshot1,
                    "screenshot2": obj.screenshot2,
                    "user_name": obj.user_name,
                    "is_blocked": obj.is_blocked,
                    "is_active": obj.is_active,
		            "user_id": obj.user_id,
                }
                if not Anketa:
                    return data
                elif Anketa:
                    return f'{data["name"]},\n\n{data["description"]}'
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
def get_ref_stat():
    try:
        with Session(autoflush=False, bind=engine) as session:
            users = session.query(User).filter(User.promocode != '').filter(User.promocode != None).all()
            return users
    except:
        return 0

        

@sync_to_async
def delete_user(user_id):
    try:
        with Session(autoflush=False, bind=engine) as session:
            session.query(User).filter(User.user_id == user_id).delete()
            session.commit()
            return 1
    except:
        return 0


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


