# lycan2
It's a different version of lycan online game. The difference is that each player have two roles. 
If one of the roles is lycan, then the player belongs to the lycan side. 
Besides its fresh rule, another advantage is that the game only requires at least 6 players.
<br>
This app is based on Django, django channels, boostrap and kendoUI.
<br>
To run the server, simply run the following two commands:
<br>
````
sudo daphne lycan.asgi:channel_layer --port 80 --bind 0.0.0.0 -v2
sudo python manage.py runworker -v2
````
