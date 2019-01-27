Please follow the installation and configuration steps  

git config --global http.sslVerify false ( in case of server ssl cert verification error)  

git clone <your project>      

e.g.   git clone  git@github.com:microservice-tsp-billing/tokenleader.git  

cd tokenleader    

virtualenv -p python3 venv  

source venv/bin/activate  

pip install --upgrade pip  

pip install -r requirement.txt ( pycrypto failed)    

ssh-keygen < press enter to select all defaults>    

python -m unittest discover tests    

to run single unit test  
python -m unittest tests.test_admin_ops.TestAdminOps.test_abort_delete_admin_user_input_not_yes  

register an admin user   
 ./tokenadmin.sh list  -a  
 ./tokenadmin.sh list  -a  -u admin -e admin@itc.in -p admin  
 ./tokenadmin.sh list  -h to get help  




export FLASK_APP='app_run.py'  

flask run -p 5001  

ensure  the port  of the server is open from security group  


To generate token :  

curl -X POST -d '{"username": "admin", "password": "admin"}'  \
-H "Content-Type: Application/json"  localhost:5001/token/gettoken

To verify token:  
 curl -H  "X-Auth-Token:<paste toekn here>"  localhost:5001/token/verify_token  


for db migration   

flask db init   
flask db migrate -m < COMMENT >  
flask db upgrde   