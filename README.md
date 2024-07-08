# Safe  Face
Generate unique avatars and swap their face onto photos and videos.

## Install: 
```
python3 -m venv .venv \
source .venv/bin/activate \
pip install -r requirements.txt
```
```
npx tailwindcss -i ./static/src/input.css -o ./static/src/output.css --watch
```
## Run: 
```
python3 manage.py migrate
```

```
python3 manage.py runserver
```


### To add default images to the gallery:
- Add your default images (must be PNG) to the `media/default_images` folder


## About
#### Backend Development
- Python with Django
   - Handles user authentication, image processing, and data management.
#### Web Development
- HTMX
   - Dynamic and interactive web application, enabling real-time updates without full page reloads.
#### Database
- SQL (SQLite)
   - Efficient, reliable data storage and management, facilitating seamless integration with Django.
#### APIs and Models
- Image Generation: [Mobius](https://huggingface.co/Corcelio/mobius) from Hugging Face
  - Ensures domain-agnostic debiasing and generates high-quality avatars.
- Face Swapping: [Face Fusion](https://github.com/facefusion/facefusion) from GitHub
  - Provides high-quality face swaps, maintaining user privacy and data security.
