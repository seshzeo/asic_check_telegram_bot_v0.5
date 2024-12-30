from datetime import datetime
import requests


class Endpoint(): 
    __cgi = '/cgi-bin/'
    STATS = __cgi + 'stats.cgi'
    REBOOT = __cgi + 'reboot.cgi'
    LOG = __cgi + 'log.cgi'
    HLOG = __cgi + 'hlog.cgi'
    SYS_INFO = __cgi + 'get_system_info.cgi'
    POOLS = __cgi + 'pools.cgi'
    SUMMARY = __cgi + 'summary.cgi'
    CHART = __cgi + 'chart.cgi'
    MAIN = '/'


# Нужно представление асика в виртуальной форме:
#   необходим доступ к тнформации асика,
#   необходимо перезагружать асик
#   необходимо прописывать пулы
#   и т.д.
# В общем нужна вся работа с API

class ASICview(object):
    def __init__(self, url: str, headers: dict, min_hash: int = 0, max_temp: int = 85) -> None:
        self._url = url
        self._headers = headers
        self._last_update = datetime(1990, 5, 5, 15, 45, 0)
        self._state = dict()
        self.min_hash = min_hash
        self.max_temp = max_temp
    
    
    def get_name(self) -> str:
        return self._url.split('.')[0].split('//')[-1]

    def update_state(self):
    # хранит как информацию о состояние асика или ошибку, если получение данных произошло
    # не успешно
        try:
            responce = requests.get(url=self._url + Endpoint.STATS, headers=self._headers)
        except Exception as e:
            self._state['error'] = str(e)
            return

        if responce.status_code != 200:
            title = responce.text.split('</title>')[0].split('<title>')[-1]
            self._state['error'] = title
            return
        if 'Socket connect failed: Connection refused' in responce.text:
            # self._state['error'] = 'Socket connect failed: Connection refused'
            self._state['error'] = responce.text
            return
        
        # Данный response возвращает json, в котором есть статус асика.
        # json_['STATUS']['STATUS']. выдает строку 'S','W' или еще что-то.
        # По хорошему это тоже надо обработать
        
        json_ = responce.json()
        status = json_['STATUS']
        info = json_['INFO']
        stats = json_['STATS'][0]
        
        self._state = {
            'asic_type' : info['type'],
            'hash5s' : float(stats['rate_5s']),
            'is_valid' : self._label_hash(float(stats['rate_5s'])),
            'units' : stats['rate_unit'],
            'hash_avg' : int(stats['rate_avg']),
            'frequency_avg' : float((
                stats['chain'][0]['freq_avg'] +
                stats['chain'][1]['freq_avg'] +
                stats['chain'][2]['freq_avg'] ) / 3),
            'temp1' : (stats['chain'][0]['temp_chip'][0], stats['chain'][0]['temp_chip'][3]),
            'temp2' : (stats['chain'][1]['temp_chip'][0], stats['chain'][1]['temp_chip'][3]),
            'temp3' : (stats['chain'][2]['temp_chip'][0], stats['chain'][2]['temp_chip'][3]),
            'fans' : stats['fan']
        }
       
    
    def get_state(self) -> dict:
        self.update_state()
        return self._state
        
    
    def _label_hash(self, hashrate: int | float) -> str:
        return '🟢' if hashrate > self.min_hash else '🔴'
        
        
    def __str__(self) -> str:
        return self.get_message()

    
    def get_message(self) -> str:
        self.update_state()
        if 'error' in self._state:
            return f'''
[{self._url}]
🔴 Не удалось получить данные.
{self._state['error']}

                    '''
        else:
            asic_type, is_valid, hash5s, units, hash_avg, freq, temp1, temp2, temp3, fans = \
            self._state['asic_type'], self._state['is_valid'], self._state['hash5s'], self._state['units'], \
            self._state['hash_avg'], self._state['frequency_avg'], self._state['temp1'], self._state['temp2'], \
            self._state['temp3'], self._state['fans']
            return f'''
[{self._url}]
Rig: {asic_type}
  Хэш 5 сек: {is_valid} {hash5s} {units}
  Хэш средний: {hash_avg} {units}
  Частота: {freq}
  Температура:
      {temp1[0]} - {temp1[1]} градусов
      {temp2[0]} - {temp2[1]} градусов
      {temp3[0]} - {temp3[1]} градусов
  Обороты куллеров:
      Вход: {fans[0]} - {fans[1]} об/мин
      Выход: {fans[2]} - {fans[3]} об/мин
                    
                '''
        
    
    def reboot(self) -> str:
        responce = requests.get(url=self._url + Endpoint.REBOOT, headers=self._headers)
        return responce.status_code


    def update_min_hash(self, hash: int) -> None:
        if hash >= 0:
            self.min_hash = hash
        else:
            raise ValueError("hash must be positive number")
        
    def update_max_temp(self, max_temp: int) -> None:
        if max_temp >= 0:
            self.max_temp = max_temp
        else:
            raise ValueError("max_temp must be positive number")


def debug():
    from utils import deserialize_miners
    
    miners = deserialize_miners()
    asics = miners['2087011410']
    # print(ml7.get_state())
    ml7 = asics[0]
    print(ml7)
    print('last update', ml7._last_update)
    print('online', ml7._online)
    # print(ml7.reboot())
    asics_status = [ asic.get_state() for asic in asics ]
    print("asics_status")
    print()
    print()
    print(*asics_status)


def debug2():
    import json

    with open('user_data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    volsk_asic_data = data["1054244799"][0]
    asic = ASICview(headers=dict(volsk_asic_data["headers"]), url=volsk_asic_data["url"], min_hash=6000)
    print(asic.get_message())
    
    
if __name__ == '__main__':
    # debug()
    debug2()