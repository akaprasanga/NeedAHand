# Need A Hand
##### A GAME THAT YOU CAN CONTROL WITH YOUR HAND GESTURES
Lets leverage the a power of hand in games. No more clicks, and no more button press. We can now just play games with the gestures.

**Need A Hand** is a platform game where you can control the actions using your hand gestures pointing towards the webcam.

### Snap Shots
![Alt text](app/static/img/needahand_preview.JPG?raw=true "Title")
![Alt text](app/static/img/portfolio/game_3a.jpg?raw=true "Title")

### Quickstart Guide for Local Development

First clone this repository through 

`https://github.com/akaprasanga/NeedAHand`

cd into the `/app` folder

`python3 -m pip install -r requirements.txt`

edit line 29 the `main.py` file to either the URL of the cocalc server you are on or `localhost` if you are running it on your own PC

Then, clone ultralytics yolov5 in the app folder, by running 

`git clone https://github.com/ultralytics/yolov5`
`pip install -r yolov5/requirements.txt`

Run

 `python3 -m main`

to start the server on local, most changes while developing will be picked up in realtime by the server
