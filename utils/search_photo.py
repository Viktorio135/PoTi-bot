from PIL import Image
import imagehash, os
from dataBase.db_commands import get_list_of_users_for_spam_db, get_user_by_id

async def compare_images(image_path, tolerance=5):

    img1 = Image.open(image_path)
    list_of_profiles = await get_list_of_users_for_spam_db(is_admin_search=True)
    for user in list_of_profiles:
        if os.path.exists(f'static/users_photo/{user}_1.jpg'):
            img2 = Image.open(f'static/users_photo/{user}_1.jpg')
            hash1 = imagehash.average_hash(img1)
            hash2 = imagehash.average_hash(img2)
            similarity = 1 - (hash1 - hash2) / len(hash1.hash) ** 2
            similarity_percent = similarity * 100
            if similarity_percent >= 100 - tolerance:
                
                return f"Фотография пользователя {user} похожа на {similarity_percent:.2f}%.", user
        if os.path.exists(f'static/users_photo/{user}_2.jpg'):
            img2 = Image.open(f'static/users_photo/{user}_2.jpg')
            hash1 = imagehash.average_hash(img1)
            hash2 = imagehash.average_hash(img2)
            similarity = 1 - (hash1 - hash2) / len(hash1.hash) ** 2
            similarity_percent = similarity * 100
            if similarity_percent >= 100 - tolerance:
                
                return f"Фотография пользователя {user} похожа на {similarity_percent:.2f}%.", user
        
    return "Пользователей с таким фото не обнаружено", None


