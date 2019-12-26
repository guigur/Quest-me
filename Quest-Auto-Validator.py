import requests
import json
import datetime
from bs4 import BeautifulSoup

with open('settings.json', encoding='utf-8') as json_file:
    settings = json.load(json_file)

with open('codes.json', encoding='utf-8') as json_file:
    codes = json.load(json_file)

with open('users.json', encoding='utf-8') as json_file:
    users = json.load(json_file)


def get_quest_token(codes_list):
    today = datetime.date.today()
    format_str = '%d-%m-%Y'
    for entry in codes_list['quest']:
        date_start = datetime.datetime.strptime(entry['start'], format_str).date()
        date_end = datetime.datetime.strptime(entry['end'], format_str).date()
        if (today >= date_start) and (today <= date_end):
            print("today token: " + entry['code'])
            return entry['code']
    return


def get_user(users_list, nom):
    for user_entry in users_list['users']:
        if user_entry['nom'] == nom:
            print("nom: " + user_entry['prenom'])
            return user_entry
    return


def validate(session, token, user):
    url_validation = settings['url'] + "/saisiepresence.php"
    periode_obj = get_periode()
    periode = periode_obj['period_id']
    params_validation = {
        'dateconnexion': date_connexion(),
        'codeeval': token,
        'session': session,

        'filiere_ii': user['filiere_ii'],
        'civilite': user['civilite'],
        'nom': user['nom'],
        'prenom': user['prenom'],
        'email': user['email'],
        'entreprise': user['entreprise'],
        'filiere': user['filiere'],
        'distance': user['distance'],
        'pc': user['pc'],

        'periode': periode,
        'submit': "Signer"
    }
    r = requests.post(url=url_validation, params=params_validation)
    soup_validate = BeautifulSoup(r.text, 'html.parser')
    return soup_validate.find('td', {'class': 'stitre'}).text


def get_session(url, token):
    params_session = {
        'dateconnexion': date_connexion(),
        'codeeval': token,
        'submit': 'Valider'
    }
    r = requests.post(url=url, params=params_session)
    soup_session = BeautifulSoup(r.text, 'html.parser')
    session = soup_session.find('input', {'name': 'session'})['value']
    print("session:" + session)
    return session


def date_connexion():
    date_today = datetime.date.today()
    date_str_format = date_today.strftime('%Y-%m-%d')
    return date_str_format


def get_periode():
    now_time = datetime.datetime.now().time()
    for entry_time in settings['window_period']:
        start_time = datetime.datetime.strptime(entry_time['start'], '%H:%M:%S').time()
        stop_time = datetime.datetime.strptime(entry_time['stop'], '%H:%M:%S').time()
        if time_in_range(start_time, stop_time, now_time):
            print("c'est la période " + entry_time['name'] + " : " + entry_time['period_id'])
            return entry_time
    return


def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


token_quest = get_quest_token(codes)
user = get_user(users, "PLACE")
session_code = get_session(settings['url'], token_quest)
print(validate(session_code, token_quest, user))