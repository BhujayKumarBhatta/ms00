echo "****Remove old virtual environment and old files****"
DIR=~/venvp3
if [ -d "$DIR" ]; then
	printf '%s\n' "Removing venv old ($DIR)"
	rm -rf "$DIR"
fi
chown jenkins /tmp/*.db
rm -f /tmp/auth.db
echo "****Create and run Virtual environment****"
virtualenv -p python3 ~/venvp3
source ~/venvp3/bin/activate
pip install --upgrade pip
echo -e "\n\n\n" | ssh-keygen -t rsa
pip install -r ~/tokenleader-pipe/requirement.txt
cd ~/tokenleader-pipe
rm -rf migrations
echo "****Run unit test****"
python3 -m unittest discover tests
export FLASK_APP=app_run.py
echo "****Migrate DB****"
flask db init
flask db migrate -m "DB Migration"
flask db upgrade
echo "****Run Token Service****"
nohup flask run --port=9898 & 
export FLASK_APP=app_register_login_user.py
echo "****Run CURD Service****"
nohup flask run --port=9999 &
sleep 30
echo "****Run UI test****"
python3 tokenuitest.py