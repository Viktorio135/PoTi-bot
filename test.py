def end_registration_kb(data=''):
    string = ''
    if data != '':
        count = 0
        for i in data:
            if len(data)-1 != count:
                string += f'{data[i]}:'
                count+=1
            else:
                string += f'{data[i]}'
    print(string)

end_registration_kb({
        "name": 0,
        "sex": 1, 
        "age": 2, 
        "description": 3, 
        "university": 4, 
        "education": 5, 
        "speciality": 6, 
        "course": 7, 
        "photos": 8
        })