# pharmik-backend

All the backend business logic connected to the Pharmik project. This is basically a Django project running Django REST Framework.

## Dependencies

- Postgres: `apt install postgresql-15`
- Redis: `apt install redis-server`

## Running docker

Build the image

```
docker build -t djangoapp .
```

Run the image

```
docker run --net=host -d -p 8000:8000 djangoapp
```

See running containers

```
docker ps
```

Jump into shell in container

```
docker exec -it <name> /bin/bash
```

Stop the container

```
docker stop <name>
```

---

## Development server

---

**SSH Login**

**TIP:** Ask Faisal to give you access to the development server.

**TIP:** Paste the snippet below in your ~/.ssh/config file, but remember to change to your user and the path to your identityfile (SSH private key)

    Host *
    IdentitiesOnly yes
    ServerAliveInterval 60

    host examplehost
    	hostname test.example.com
    	user johndoe
    	port 1919

**Cloning your fork**

    cd ~
    git clone github.com:johndoe/projectile.git project

**Setting up a virtualenv**

virtualenv is a nifty tool for creating virtual environments for Python projects

    cd ~
    python3 -m venv env
    source ~/env/bin/activate

If you find it tedious to do the above everytime you log in you can copy the snippet below in to a file named _~/.bashrc_ or _~/.bash_profile_ and You will automatically land in the project folder everytime you log in with the virtualenv activated.

    source ~/env/bin/activate
    cd ~/project

Try logging out from your ssh session and log in to see if the snippet above works.

**Install the Python dependencies for the project**

Make sure your virtualenv is active, the name of the env wrapped in round brackets should appear next to your username@hostname in the terminal.

    (env)johndoe@uduntu:~$

And then run

    pip install -r ~/project/requirements/development.txt

Make sure that your .env is properly set

    nano .env

**Run the test server**

    cd ~/project
    python projectile/manage.py runserver 0:8000

You can now visit 127.0.0.1:8000 on your browser and see that the project is running.
