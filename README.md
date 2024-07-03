# Safe  Face
Generate an AI avatar then swap their face onto your photos and videos.

## Install: 
python3 -m venv .venv \
source .venv/bin/activate \
pip install -r requirements.txt

npx tailwindcss -i ./static/src/input.css -o ./static/src/output.css --watch

## Run: 
```
python3 manage.py migrate
```

```
python3 manage.py runserver
```


### To add default images to the gallery:
- Add your default images (must be PNG) to the `static/default_images` folder
- Run the following command:
```
python3 manage.py load_default_images
```

tygil has a tiny worm
