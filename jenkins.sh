#cd /root/tokenleader-build;source /root/venvp3/bin/activate;/root/venvp3/bin/python3  -m unittest discover /root/tokenleader-build/tests
rm -rf ~/venvp3
virtualenv -p python3 ~/venvp3
#root/venvp3/bin/python3 ~/venvp3/bin/activate
source ~/venvp3/bin/activate
pip install --upgrade pip
pip install -r ~/tokenleader-pipe/requirement.txt
#cd /root/tokenleader-pipe;/root/venvp3/bin/python3  -m unittest discover /root/tokenleader-pipe/tests
cd ~/tokenleader-pipe
python3  -m unittest discover tests
