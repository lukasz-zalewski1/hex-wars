# hex-wars (2019)

## Description
This game is inspired by an old flash game called [Dicewars](https://www.gamedesign.jp/games/dicewars/).

<br>

The goal of the game is to conquer all enemy fields. You play as **Red** and fight other colorful enemies. 

The game is turn based. Each turn you can make as many moves as you want. In each move you can select your attacking field and battle against adjacent enemy fields. Each field has a number, which represents power of the forces on it - *Dice*. Each battle the *Dice* are rolled. If you managed to get better a result than the enemy, you take his field and move all but 1 of your *Dice* forces there. If you have lost the battle, you lose all but 1 of your *Dice* forces on your attacking field. After you make all of your moves, then all of your enemies will take their turn. At the end of every turn forces of all players grow depending on the number of their adjacent fields. 

**Hex-Wars** is a fully customizable experience. You can adjust size of the map, number of players, how many sides *a die* has or how many of them can fill into a single field.

## Use

Clone the repository and run the following command:
```ps
pip install -r requirements.txt
python main.py
```

## Controls

**LMB** - Select attacking and attacked fields, adjust settings  
**RMB** + **Mouse Move** - Move map  
**Mouse Scroll** - Zoom In / Out  
**Space** - End of your turn  
**A** - Generate a new map  
**Escape** - Exit the application

