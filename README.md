# cs311-tsp-webapp

## How to run the application?

Go to this [link](https://github.com/lyt1602/cs311-tsp-webapp) and clone this project

Make sure you already have:

- Python (preferably python-3.10.6)
- Virtual Environment ([venv](https://docs.python.org/3/library/venv.html))

**Note**: This project was created on Ubuntu. Make sure you are in the root folder of the project. If run this on window, you will need to modify the paths in `./mypack.py` and `./app/app.py` because the path in these files were made for linux system in mind.

Create a virtual environment and use it

```bash
# Create a virtual environment
python3 -m venv env

# activate the environment (linux)
source env/bin/activate

# activate the environment (powershell)
env\Scripts\Activate.ps1
```

Install all requirement

```bash
pip install -r requirements.txt
```

Run the application

```bash
# Make sure you are in the root directory of the project
flask run
```

You can check the app out on [http://127.0.0.1:5000](http://127.0.0.1:5000)

Note: If you have trouble creating video, you may need to install ffmpeg on your OS.