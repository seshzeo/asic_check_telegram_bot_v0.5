from asic_view import ASICview
import json


class WatchDogValues():
    HASHRATE = {
        "min": 0,
        "max": 10000,
        "update": lambda asic, hash: asic.update_min_hash(hash),
        "get": lambda asic: asic.min_hash,
        "unit": lambda asic: asic.get_state()['units'],
    }
    
    TEMP = {
        "min": 25,
        "max": 89,
        "update": lambda asic, temp: asic.update_max_temp(temp),
        "get": lambda asic: asic.max_temp,
        "unit": lambda _: "℃",
    }


def deserialize_miners(json_file: str = '/root/Scripts/python-bot/asic_check_telegram_bot_v0.5/user_data.json') -> dict:
    with open(json_file, 'r') as json_file:
        miners = json.load(json_file)
    
    # miners содержит ключ - id аккаунта telegram, а значение - список данных асиков - url, headers и min_hash
    asic_views = {}
    for id, asics in miners.items():        
        if id not in asic_views:
            asic_views[id] = []

        for asic in asics:
            asic_views[id].append(ASICview(**asic))

    return asic_views


def check_valid_user(id: str | int, json_file: str = '/root/Scripts/python-bot/asic_check_telegram_bot_v0.5/user_data.json') -> str:
    with open(json_file, 'r') as json_file:
        miners = json.load(json_file)

    if str(id) in miners.keys():
        print(f"{id} найден") #debug
        return str(id)
    print(f"{id} не найден") #debug
    return f"Пользователь {str(id)} не найден" 


def change_watchdog_values(update, context, miners, update_type):
    min, max, change, get, unit = update_type["min"], update_type["max"], update_type["update"], update_type["get"], update_type["unit"]

    answer = ''
    asics = miners[str(update.effective_chat.id)]

    if not context.args:
        answer = '\n'.join([ asic._url + ' ' + str(get(asic)) + ' ' + unit(asic) for asic in asics])
    else:
        input_value = int(context.args[0])
        if input_value < min or input_value > max:
            answer = f'Неверное значение. Текущее значение {get(asics[0])}'
        else:
            context.bot_data['min_hash'] = input_value
            current = input_value
            for asic in asics:
                change(asic, current)
            answer = f'Пороговое значение изменено на {input_value}'
    return answer
    

if __name__ == '__main__':
    json_file = 'user_data.json'
    miners = deserialize_miners(json_file)
    print(miners)

    print(check_valid_user('2087011410'))
    print(check_valid_user('1054244799'))
    print(check_valid_user('0'))

    print(WatchDogValues.TEMP["get"](ASICview('url', {'hello': 'world'}, 0, 80)))
