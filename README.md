Please follow the installation and configuration steps

virtualenv -p python3 ~/venvp3

source ~/venvp3/bin/activate

git config --global http.sslVerify false ( in case of server ssl cert verification error)

git clone <your project>

cd tokenleader

pip install --upgrade pip

pip install -r requirement.txt ( pycrypto failed)

ssh-keygen < press enter to select all defaults>

python -m unittest discover tests

export FLASK_APP='app_run.py'

flask run -p port number 

ensure  the port  of the server is open from security group


To generate token :

curl -X POST -d '{"username": "susan", "password": "mysecret"}'  \
-H "Content-Type: Application/json"  localhost:5000/token/gettoken

To verify token:

curl -X POST -d '{"auth_token":"<paste the token here> "}'  -H "Content-Type: Application/json"  localhost:5000/token/verify_token


for db migration 

flask db init 
flask db migrate -m < COMMENT >
flask db upgrde 