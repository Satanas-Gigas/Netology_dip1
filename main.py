import requests
import datetime
from tqdm.auto import tqdm
import time
import json

class VK:
   def __init__(self, vk_prof_id, vk_token):
       self.token = vk_token
       self.id = vk_prof_id
       self.version = '5.131'
       self.params = {'access_token': self.token, 'v': self.version}

   def photo_info(self):
       """Функция получения params для запросов с ВК"""
       url = 'https://api.vk.com/method/photos.get'
       params = {"owner_id": self.id,
                 "album_id": "profile",
                 "rev": 1,
                 "extended": 1,
                 'photo_sizes': 1,
                 }
       request = requests.get(url, params={**self.params, **params}).json()['response']

       """Получение фоток с ВК"""
       url_list = []
       like_list = []
       json_report = []
       ret_data=[]

       for it_em in request['items'][:5]:
           max_dpi = 0
           name = str(it_em['likes']['count'])

           if name in like_list:
               time_ph = datetime.datetime.fromtimestamp(it_em['date'])
               str_time = time_ph.strftime('date_%Y-%m-%d_time_%H-%M-%S')
               name += '_' + str_time

           like_list.append(name)

           for size_photo in it_em['sizes']:
               photo_in_array = size_photo['height'] * size_photo['width']
               max_url = size_photo['url']
               size_type = size_photo['type']

               if photo_in_array > max_dpi:
                   max_dpi = photo_in_array
                   max_url = size_photo['url']
                   size_type = size_photo['type']

           url_list.append(max_url)

           """Создание json файла"""
           json_report.append({"file name": name + ".jpeg", "size": size_type})

           """Запись json файла"""

       with open('YA_VK.json', 'w') as outfile:
           json.dump(json_report, outfile)

       ret_data.append(url_list)
       ret_data.append(like_list)
       return ret_data

class YA(VK):

   def __init__(self, ya_prof_token):

       super().__init__(vk_prof_id, vk_token)
       """Метод для получения params на Я-диск"""

       self.token = ya_prof_token
       self.url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
       self.headers = {'Authorization': self.token}
       self.folder = "Yan_Api_VK"

       """Создание папки в ЯДИСКЕ и загрузка туда фоток"""

   def upload(self):
       url = "https://cloud-api.yandex.net/v1/disk/resources"
       params = {'path': f'{self.folder}', 'overwrite': True}

       if requests.put(url, headers=self.headers, params=params).status_code == 201:
           print(f'\nПустая папка Yan_Api_VK создана в ЯДИСКЕ\n')
       else:
           requests.delete(url, headers=self.headers, params=params)
           requests.put(url, headers=self.headers, params=params)
           print(f'\nПапка Yan_Api_VK была в ЯДИСКЕ, для проверки работоспособности программы, мы удалили её и создали заново\n')

       photo_list = super().photo_info()
       photo_dictionary = dict(zip(photo_list[1], photo_list[0]))

       """Процесс загрузки с индикатором"""

       photo_bar = tqdm(photo_dictionary.items(), desc="ЗАГРУЗКА")

       for key, value in photo_bar:
           time.sleep(0.1)
           params = {'path': f'{self.folder}/{key}',
                     'url': value,
                     'overwrite': 'false'}
           requests.post(self.url, headers=self.headers, params=params)

       response = requests.post(self.url, headers=self.headers, params=params)

       if response.status_code == 409:
           print("Не удается обработать запрос из-за конфликта в текущем состоянии ресурса.\nЗапустите программу ещё раз")

       print("Статус операции загрузки файлов на ЯДИСК: ", response.status_code)


if __name__ == '__main__':
    vk_prof_id = input("Введите id пользователя vk: ")
    vk_token = input("Введите token приложения vk: ")
    ya_prof_token = input("Введите токен с Полигона Яндекс.Диска ")
    my_VK = VK(vk_prof_id, vk_token)
    my_VK.photo_info()
    my_YA = YA(ya_prof_token)
    my_YA.upload()
