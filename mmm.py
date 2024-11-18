if (report_data["screenshot1"] != '') and (report_data["screenshot2"] != ''):
            media.attach_photo(types.InputFile(
                f'static/users_photo/{report_data["user_id"]}_1.jpg'),
                f'{report_data["name"]}\n{roles}\n{report_data["description"]}')
            media.attach_photo(types.InputFile(f'static/users_photo/{report_data["user_id"]}_2.jpg'), caption=f'Пользователь {user_id} подал жалобу на {report_user_id} по причине "{data["cause"]}"\n\n{report_data}')
            await bot.send_media_group(
                admin_id, 
                media=media,
            )

                
        elif (report_data["screenshot1"] != '') and (report_data["screenshot2"] == ''):
                media.attach_photo(types.InputFile(
                    f'static/users_photo/{report_data["user_id"]}_1.jpg'),
                    caption=f'Пользователь {user_id} подал жалобу на {report_user_id} по причине "{data["cause"]}"\n\n{report_data}')
                await bot.send_media_group(
                    admin_id, 
                    media=media,
                )

        else:
                await bot.send_message(
                    admin_id,
                    f'Пользователь {user_id} подал жалобу на {report_user_id} по причине "{data["cause"]}"\n\n{report_data}'
                ) 