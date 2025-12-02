# Aurora Telegram bot YouTube extractor
This is a simple **AGENTIC** telegram bot that downloads youtube video, audio and subtitles in english and russian, it is also scaleable to add all available languages.

With this bot you can download videos in 4 different qualities (144p - 360p - 720p - 1080p)

You can also chat with a chat bot and give it different behavoir and tasks in **prompts.py** file

**Before all of this steps you should have ( a Ubuntu VPS server) and ( telegram bot with its API ) and ( a telegram account with a username ) and ( a gemini API )**

**Folow this steps:**

# Deploy on ubuntu server
1. Install python, pip, git
```
sudo apt install python3 python3-pip python3-venv git -y
```
2. Clone repository
```
git clone https://github.com/ArashPoorazam/youtube_extractor
```
3. Create .env file for yout API keys
```
touch .env
nano .env
```
4. Fill the file like this with your own API keys then save and exit
```
# TELEGRAM BOT API KEY
API_KEY=
# GEMINI API KEY
GEMINI_API_KEY=
# YOUR TELEGRAM USERNAME
ADMIN_USERNAME=
```
5. Install root requirements 
```
sudo apt install -r req.txt
```
6. Create virtual environments and install the packages
```
python3 -m venv venv
source venv/bin/activate
pip install -r venv_req.txt
deactivate
```
7. Create ststemd service file 
```
sudo nano /etc/systemd/system/telegram-youtube-bot.service
```
8. In the file paste this and change it to your own username and cloned path.
if you cloned from root dont change it!
WARNING: Running as 'root' is generally discouraged for security.
```
[Unit]
Description=Telegram YouTube Extractor Bot
After=network.target

[Service] 
User=root
EnvironmentFile=/root/youtube_extractor/.env
WorkingDirectory=/root/youtube_extractor
ExecStart=/root/youtube_extractor/venv/bin/python main.py
StandardOutput=syslog
StandardError=syslog
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```
9. Reload, start and enable ststemd service
```
sudo systemctl daemon-reload
sudo systemctl start telegram-youtube-bot.service
sudo systemctl enable telegram-youtube-bot.service
```
Everything should be fine and you can use the bot it should work just fine.

# Update
If any new update happens just pull from this repository and restart from your **cloned directory**.
```
git pull origin main
sudo systemctl restart telegram-youtube-bot.service
```
