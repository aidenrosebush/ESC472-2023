# ESC472-2023

# Files

`convertShp2Array.py` (Jasper & Jondy) is the python file containing functions for handling data import into numpy arrays

`viewshed_los_fast.py` (Aiden) is the python file containing functions for generating the visibility plume as a list of visible points in the matrix

`rogers_centre.py` (Jasper & Aiden) is an example script importing the functions from both to generate a visibility plume for the Roger's centre

# Dependencies

    python3 -m pip install tcod pyproj

# Run Example Script for Rogers' Centre

Place data from <https://utoronto-my.sharepoint.com/:f:/r/personal/maxwell_fingold_mail_utoronto_ca/Documents/ESC472_Group1_2023/Data?csf=1&web=1&e=WxpMRD> into same directory as script.

    python3 ./rogers_centre.py
