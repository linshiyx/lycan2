# lycan2
It's a different version of lycan online game. The difference is that each player have two rolls. 
If one of the rolls is lycan, the the player belongs to the lycan side. 
Besides its fresh rule, another advantage is that the game only requires at least 6 players, making it easy to start.
<br>
This app is based on Django, django channels, boostrap and kendoUI.
<br>
To run the server, simply use the following two commands:
<br>
````
sudo daphne MyProject.asgi:channel_layer --port 80 --bind 0.0.0.0 -v2
sudo python manage.py runworker -v2
````
