
1. Start azure VM
    ```
    ssh -i private key path life-app@20.124.225.196
    ```
2. clone repository
    ```
    git clone https://github.com/drudgery/lifetestapp.git
    ```
3.  cd to folder name(repo name)
    ```
    cd lifetestapp
    ```
4. create python virtual environment(venv) 
    ```
    python3 -m venv venv
    ```  
5. activate python virtual environment(venv) 
    ```
    source venv/bin/activate
    ```
6. install all dependencies from requirements.txt
    ```
    pip install requirements.txt
    ```
7. Setup mongodb
    ```
    sudo apt-get install mongodb
    ```
    Check the MongoDB Version and its status -
    ```
    mongod --version

    sudo systemctl status mongodb
    ```
8. run the application
    ```
    flask run -h 0.0.0.0
    ```
    ```
    nohup flask run -h 0.0.0.0 &
    ```
9. In browser address bar
    ```
    20.124.225.196:5000
    ```
10. view mongodb in GUI: install mongodb compass (not working in azure VM)
    - https://www.digitalocean.com/community/tutorials/how-to-use-mongodb-compass
    - mongodb from terminal
    https://docs.mongodb.com/manual/tutorial/getting-started/       