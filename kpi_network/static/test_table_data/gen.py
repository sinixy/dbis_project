import names
import random as r
import csv

USERS_CNT = 100
CHANNELS_CNT = 10
CHANNEL_MEMBERS_CNT = 20
CHANNEL_POSTS_CNT = 30
CONTACTS_CNT = 1000
MESSAGES_PER_CONTACT_CNT = 5

users = []
students = []
instructors = []

for i in range(1, USERS_CNT + 1):
	name = names.get_full_name()
	numbers = r.randint(0, 10000)
	login = f'{name.replace(" ", "")}{numbers}'
	utype = 2 if r.uniform(0, 1) > 0.7 else 1
	if utype == 1:
		students.append({
			'id': i,
			'group': 'KM-' + str(r.randint(1, 100)),
			'department': 'FAM'
			})
	else:
		instructors.append({
			'id': i,
			'department': 'FAM'
			})
	users.append({
		'login': login,
		'password': login,
		'name': name,
		'utype_id': utype
		})


channels = []
user_channel = []
user_channel_check = []
posts = []

for i in range(1, CHANNELS_CNT + 1):
	creator_uid = r.randint(1, USERS_CNT)
	creator = users[creator_uid - 1]
	name = f"{creator['login']}'s channel"
	description = f"Yo-yo-yo {creator['login']}'s here!"

	channels.append({
		'name': name,
		'description': description
		})

	user_channel.append({
		'uid': creator_uid,
		'cid': i,
		'access_level': 1
		})

	channel_members_cnt = 1
	while channel_members_cnt < CHANNEL_MEMBERS_CNT:
		random_user_uid = r.randint(1, USERS_CNT)
		relationship = f'{random_user_uid}-{i}'
		if random_user_uid == creator_uid:
			continue
		if relationship in user_channel_check:
			continue
		user_channel.append({
			'uid': random_user_uid,
			'cid': i,
			'access_level': 0
		})
		user_channel_check.append(relationship)
		channel_members_cnt += 1


	channel_posts_cnt = 1
	while channel_posts_cnt < CHANNEL_POSTS_CNT:
		random_user_uid = r.randint(1, USERS_CNT)
		posts.append({
			'cid': i,
			'text': f'Lorem ipsum {channel_posts_cnt}',
			'author_id': random_user_uid
		})
		channel_posts_cnt += 1


contacts = []
messages = []
contact_check = []
contacts_cnt = 0
while contacts_cnt < CONTACTS_CNT:
	u1 = r.randint(1, USERS_CNT)
	u2 = r.randint(1, USERS_CNT)
	if u1 == u2:
		continue
	relationship = f'{u1}-{u2}'
	if relationship in contact_check:
		continue
	contacts.append({
		'uid_1': u1,
		'uid_2': u2
		})
	contacts.append({
		'uid_1': u2,
		'uid_2': u1
		})
	contact_check.append(relationship)
	contact_check.append(f'{u2}-{u1}')
	contacts_cnt += 1
	for i in range(1, 2*(MESSAGES_PER_CONTACT_CNT) + 1):
		if i % 2 == 0:
			messages.append({
				'sender': u1,
				'receiver': u2,
				'text': 'Lore Ipsum?'
				})
		else:
			messages.append({
				'sender': u2,
				'receiver': u1,
				'text': 'Lore Ipsum!'
				})

tables = {
	'user': users,
	'instructor': instructors,
	'student': students,
	'channel': channels,
	'user_channel': user_channel,
	'post': posts,
	'contacts': contacts,
	'message': messages
}
for table, data in tables.items():
	with open(f'{table}.csv', 'w', newline='') as file:
		fieldnames = data[0].keys()
		writer = csv.DictWriter(file, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(data)