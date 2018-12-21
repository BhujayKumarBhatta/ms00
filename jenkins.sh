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
python3 -m unittest discover tests