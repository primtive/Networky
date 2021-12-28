import requests
import discord
import json
import os
import codecs
from discord_slash import SlashContext

cookies = {
	'_ym_d': '1630922337',
	'_ym_uid': '1630922337421947584',
	'session-cookie': '16c4e1d35569e890e0178c4fbeb261f5cf53d466e46b125a89255f125bc11f385d13144ec67640863764cce5dff9410a',
	'_ym_isad': '1',
	'PHPSESSID': 'f182cd32d914476a01be1945465576d4',
	'csrf-token-name': 'csrftoken_edu',
	'X1_SSO': '61cafc269bd11600062b1871',
	'csrf-token-value': '16c4e9657454d3e8f882d22e27e0d6809225d953fb6cf18c16ce7126153990eeda48552ca5856753',
}
headers = {
	'Connection': 'keep-alive',
	'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
	'Accept': '*/*',
	'DNT': '1',
	'X-Requested-With': 'XMLHttpRequest',
	'sec-ch-ua-mobile': '?0',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
	'sec-ch-ua-platform': '"Windows"',
	'Sec-Fetch-Site': 'same-origin',
	'Sec-Fetch-Mode': 'cors',
	'Sec-Fetch-Dest': 'empty',
	'Referer': 'https://de.edu.orb.ru/edv/index/participant',
	'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
}
class_id = 'B427F5E714044404AA17FA6F69F89D9C'

def get_diary(date: str):
	params = (('date', date),)
	response = requests.get('https://de.edu.orb.ru/edv/index/diary/D3BA0AF97355458780F1D5372C3E7B5C', headers=headers,
							params=params, cookies=cookies)
	
	return response


def get_student_id(name: str, class_id: str):
	params = (('parent', class_id),)
	response = requests.get('https://de.edu.orb.ru/er/index/lookup/PARTICIPANTFK', headers=headers, params=params,
							cookies=cookies)
	if response.status_code == 200:
		result = json.loads(response.text)
		if result['success']:
			for element in result['data']:
				if element['text'].find(name) != -1:
					return element['id']


async def get_marks(ctx: SlashContext, name: str, date_begin: str, date_end: str):
	id = get_student_id(name, class_id)
	params = (
		('GRADEFK', class_id),
		('PARTICIPANTFK', id),
		('DATE_BEGIN', date_begin),
		('DATE_END', date_end),
	)
	
	response = requests.get('https://de.edu.orb.ru/er/index/report/report/progress/participant_marks',
							headers=headers, params=params, cookies=cookies)
	if response.status_code == 200:
		filename = os.path.join(os.getcwd(), 'marks', id + '.html')
		f = open(filename, 'w')
		f.write(response.text)
		f.close()
		with codecs.open(filename, 'r', encoding="Windows-1251") as f:
			text = f.read()
		with codecs.open(filename, 'w', encoding='utf8') as f:
			f.write(text)
		await ctx.reply('Отправил оценки в лс')
		await ctx.author.send(file=discord.File(filename))
	else:
		await ctx.reply('Произшла ошибка:\n\n' + str(response.status_code) + ': ' + response.text)


async def get_final_marks(ctx: SlashContext, name: str):
	id = get_student_id(name, class_id)
	params = (
		('GRADEFK', class_id),
		('PARTICIPANTFK', id),
	)
	
	response = requests.get('https://de.edu.orb.ru/er/index/report/report/progress/participant_period_marks',
							headers=headers, params=params, cookies=cookies)
	if response.status_code == 200:
		filename = os.path.join(os.getcwd(), 'marks', id + '.html')
		f = open(filename, 'w')
		f.write(response.text)
		f.close()
		with codecs.open(filename, 'r', encoding="utf8") as f:
			text = f.read()
		with codecs.open(filename, 'w', encoding='Windows-1251') as f:
			f.write(text)
		await ctx.reply('Отправил оценки в лс')
		await ctx.author.send(file=discord.File(filename))
	else:
		await ctx.reply('Произшла ошибка:\n\n' + str(response.status_code) + ': ' + response.text)
