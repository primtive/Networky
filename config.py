import discord
import token
from rpg import RPG

# Main settings

console = True
prefix = '#'
password = '1717'
token = token.token
guild = 775211413882798120
embed_color = 0xfecc4e
hentai_lib = '2_9'
economic_file = 'save.json'
rip_image = 'https://media2.giphy.com/media/Wr2747CnxwBSqyK6xt/giphy.gif?cid=ecf05e47imcye4fyk3qnrlg2cd70lctnvovptuq5xqbrrgb9&rid=giphy.gif&ct=g'

# Default settings

default_status = discord.Status.online
default_activity_type = discord.ActivityType.watching
default_activity_text = 'за сервером'

# Economic settings

daily_coins = 100

# Answers settings

daily_error = 'Вы уже собрали ежедневную награду сегодня.'
daily_success = 'Вы собрали ежедневную награду в размере {} $'.format(daily_coins)

not_enough_money_error = 'У вас недостаточно денег для совершения операции'
role_number_error = 'Введите корректный номер роли.'
has_role_error = 'У вас уже есть эта роль.'

id_error = 'Введите корректный id предмета.'
has_item_error = 'У вас уже есть такой же или предмет лучше.'

role_perm_error = 'Эту команду могут использовать только участники с ролью {} и выше.'
owner_perm_error = 'Эту команду может использовать только владелец севера.'
upper_role_error = 'Вы не можете замутить этого человека.'
member_error = 'Укажите участника.'
password_error = 'Неверный пароль'

voting_not_found = 'Голосование не найдено.'

zero_time_error = 'Время не может быть равно нулю.'
lower_zero_time_error = 'Время не может быть меньше нуля.'

self_error = 'Вы не можете сделать это действие с собой.'
bot_error = 'Вы не можете сделать это действие с ботом.'

channel_error = 'Вы не можете использовать эту команду здесь.'

dm_help = 'Команды в лс используются для подшучивания над игроками на сервере за игровую валюту. Список команд дан тут.\n' \
          '#voicekick (Discord ID участника)  -  Отключение участника от голосового канала (200 $)\n' \
          '#voicemute (Discord ID участника) (время в секундах до 60 секунд)  -  Мут в голосовом канале, 1 сек - 50 $'

# Channels settings

main_channel = 777178643579404310
test_channel = 778543185885659156
nsfw_channel = 783617240896503818
beta_test_channel = 897432943218266133

# Roles settings

server_owner_role = 804006292812595250
admin_role = 822834353092427857
helper_role = 822834405190008833
emperor_role = 822834544830447626
deluxe_role = 822834488916312064
vip_role = 822835336480555028

muted_role = 776134417012752445

# Permissions settings

voting_perm_role = emperor_role
mute_perm_role = admin_role
call_perm_role = deluxe_role
user_info_perm_role = vip_role
