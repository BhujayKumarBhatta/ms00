DIR=~/venvp3
if [ -d "$DIR" ]; then
	printf '%s\n' "Removing venv old ($DIR)"
	rm -rf "$DIR"
fi
chown jenkins /tmp/*.db
virtualenv -p python3 ~/venvp3
source ~/venvp3/bin/activate
pip install --upgrade pip
echo -e "\n\n\n" | ssh-keygen -t rsa
pip install -r ~/tokenleader-pipe/requirement.txt
cd ~/tokenleader-pipe
rm -rf migrations
python3 -m unittest discover tests
export FLASK_APP=app_run.py
flask db init
flask db migrate -m "DB Migration"
flask db upgrade
nohup flask run --port=9898 & 
export FLASK_APP=app_register_login_user.py
nohup flask run --port=9999 &

