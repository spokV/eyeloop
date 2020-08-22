#redis-server --protected-mode no --save "" --appendonly no &
#service apache2 start
#python run_model_server.py &
python3 run_ws_server.py --host 192.168.1.192 --port 5000 --stabilize 0
