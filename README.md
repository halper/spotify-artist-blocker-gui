# spotify-artist-blocker-gui

Spotify artist blocker works only on Linux!

This project consists of two parts. First part is GUI for visualization and commanding spotify_listener.py, which enables you block any artist that occured on your playlist.

spotify_listener.py communicate with spotify application running on your computer. It gets relevant data and write it to local sql database to be shown in GUI.

You also need a database called 'spotify' with following tables and columns:

genres:id(int11),name(varchar255)

songs:id(int11),trackid(varchar255),title(varchar255),artist(varchar255),album(varchar255),genre_id(foreign,int11),cover(varchar255),restricted(tinyint1),played(smallint6),duration(int11),played_on(datetime)
