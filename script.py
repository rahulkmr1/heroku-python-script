import telepot
import time
import requests
from bs4 import BeautifulSoup as bs
import cPickle
import csv

RAHUL_ID = 931906767

# You can leave this bit out if you're using a paid PythonAnywhere account
# proxy_url = "http://proxy.server:3128"
# telepot.api._pools = {
#     'default': urllib3.ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=False, timeout=30),
# }
# telepot.api._onetime_pool_spec = (urllib3.ProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30))
# end of the stuff that's only needed for free accounts

########################
login_url = 'https://www.placement.iitbhu.ac.in/accounts/login/'

client = requests.session()
login = client.get(login_url)
login = bs(login.content, "lxml")

payload = {
	"login": "rahul.kumar.cse15@itbhu.ac.in", 
	"password": "rahulkmr", 
	"csrfmiddlewaretoken": login.input['value']
}

result = client.post(
	login_url, 
	data = payload, 
	headers = dict(referer=login_url)
)

forum = client.get("https://www.placement.iitbhu.ac.in/forum/c/notice-board/2019-20/")
soup = bs(forum.content, "lxml")


#load last message delivred to users
try:
	with open("posts.bin", "rb") as f:
		posts = cPickle.load(f);
except Exception as e:
	print e
	
	posts = soup.findAll("td", "topic-name")

	for i in range(len(posts)):
		posts[i] = posts[i].a

	posts.pop(0)
	posts.pop(0)








updated = soup.findAll('td','topic-last-post')

# updated.pop()
# updated.pop(0)
#########################

bot = telepot.Bot('940251504:AAG19YYQYtkiEOCrW0fZETvmYQSskElARcc')

# chat_ids = {RAHUL_ID}
with open("IDs.bin", "rb") as f:
	chat_ids = cPickle.load(f)
	print '#################No of IDs loaded: ', len(chat_ids) 

####### Commands ########
def start(msg):
	# with open("users.csv", "w") as f:
	# 	writer = csv.writer(f)
	# 	writer.writerow(msg['from'].values())


	bot.sendMessage(msg['chat']['id'],"Hello " + msg['from']['first_name'])

def add_cmd(chat_id, msg, *argv):
	
	if chat_id not in chat_ids:
		chat_ids.add(chat_id)
		with open("IDs.bin", "wb") as f:
			cPickle.dump(chat_ids, f);

		with open("users.csv", "a") as f:
			writer = csv.writer(f)
			writer.writerow(msg['from'].values())

		bot.sendMessage(chat_id, "Added your ID for notifications. Note that it may take upto 5 minutes to get update of a recent post")

	else:
		bot.sendMessage(chat_id, "You are already added")

def remove_cmd(chat_id, *argv):
	try:
		chat_ids.remove(chat_id)
		with open("IDs.bin", "wb") as f:
			cPickle.dump(chat_ids, f);
		bot.sendMessage(chat_id, "Removed your ID")
	except KeyError:
		bot.sendMessage(chat_id, "You are not in the list")

def allPosts(chat_id, *argv):
	msg = ''
	for i in range(len(posts)):
		msg += gen_msg(posts[i]) + '\n<b>Last Updated: </b>' + updated[i].string.encode() + '\n\n'

	bot.sendMessage(chat_id, text=msg, parse_mode="HTML")

def top(chat_id, param, *argv):
	total = 3
	if len(param) > 1 and param[1].isdigit():
		total = min(15, int(param[1]))

	msg = '.'
	for i in range(total):
		msg += gen_msg(posts[i])

	try:
		# print msg
		bot.sendMessage(chat_id, text=msg, parse_mode="HTML")
	except Exception as e:
		bot.sendMessage(chat_id, text=str(e), parse_mode="HTML")
	
#########################


command = {'/add':add_cmd, '/remove':remove_cmd, '/all':allPosts, '/recent':top}



def handle(msg):
	# print msg
	content_type, chat_type, chat_id = telepot.glance(msg)

	print msg['from']['first_name'], chat_id

	if content_type == 'text':
		if msg['text'][0] == '/':
			tokens = msg['text'].split()
			try:
				if tokens[0] == '/start':
					start(msg)
				elif tokens[0] == '/add':
					add_cmd(chat_id, msg)
				else:
					command[tokens[0]](chat_id, tokens)
			except KeyError:
				bot.sendMessage(chat_id, "Unknown command: {}".format(tokens[0]))
		
		else:
			bot.sendMessage(chat_id, "You said '{}'".format(msg["text"]))

bot.message_loop(handle)

print ('Listening ...')

# for chat_id in chat_ids:
# 	bot.sendMessage(chat_id, text='Server started', parse_mode="HTML")

bot.sendMessage(chat_id, text='Server started', parse_mode="HTML")


def gen_msg(post):
	
	string = str(post)
	string = string[:8] + '"https://www.placement.iitbhu.ac.in' + string[9:]  + '\n-----------------\n<b>Last Updated: </b>' + updated[posts.index(post)].string.encode() + '\n'
	# string += '

	post = client.get("https://www.placement.iitbhu.ac.in/" + post['href'])
	post = bs(post.content, "lxml")

	post = post.find("td", "post-content")
	# print post.contents

	for x in post.contents:
		
		if type(x) is type(post.contents[0]):
			string += x + '\n'

	post = post.find("div", "attachments").a
	if post is not None:
		tmp = '<a href=' + '"https://www.placement.iitbhu.ac.in' + post['href'] + '">'
		tmp += post.contents[1].split()[0]
		tmp += '</a>'
		string += tmp


	string += '\n\n'
	return string

def on_new():
	global updated

	global posts
	
	posts2 = soup.findAll("td", "topic-name")

	for i in range(len(posts2)):
		posts2[i] = posts2[i].a

	#find how many new posts
	
	try:
		total = posts2.index(posts[0])
	except ValueError:
		total = len(posts2)

	print total, "new posts, users = ", len(chat_ids)
	posts = posts2
	updated = soup.findAll('td','topic-last-post')

	msg = '<b>Note that you need to be logged in before opening these links, else youll see 500 error in your browser</b>\n\n'
	for i in range(total):
		msg += gen_msg(posts[i])


	for chat_id in chat_ids:
		# print "sending update to ", chat_id
		bot.sendMessage(chat_id, text=msg, parse_mode="HTML")

	#save last message delivred to users
	with open("posts.bin", "wb") as f:
		cPickle.dump(posts, f);



# Keep the program running.
def main():
	while 1:
		# bot.sendMessage(RAHUL_ID, text="Dynamic code update", parse_mode="HTML")
		global forum
		global soup
		
		try:
			forum = requests.get("https://www.placement.iitbhu.ac.in/forum/c/notice-board/2019-20/")
			soup = bs(forum.content, "lxml")

			if len(posts) == 0 or soup.td.a['href'] != posts[0]['href']:
				on_new()

		except Exception as e:
			bot.sendMessage(RAHUL_ID, text="<b>Exception:</b>\n" + str(e), parse_mode="HTML")
		# else:
		# 	bot.sendMessage(RAHUL_ID, text="Error in polling TPO forum", parse_mode="HTML")
			
		try:
			time.sleep(1000 * 60 *1)
		finally:
			# for chat_id in chat_ids:
			# 	bot.sendMessage(chat_id, text='Server closing for maintenance, you might miss updates', parse_mode="HTML")
			bot.sendMessage(RAHUL_ID, text='Server closing for maintenance, you might miss updates', parse_mode="HTML")

if __name__ == '__main__':
	main()
