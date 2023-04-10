# Representation

Main questions:

- combined betsizes and raises into the same betsize range or have the actions be separate?
- keep action types and betsizes as two different things, or have them as one e.g. [fold,check,call,bet/raise0.1,bet/raise0.25] etc.
- how to represent the blinds? raise + betsize + is_blind? currently its action is None

keeping actions and betsizes different probably means the representation will have an easier time figuring out what is going on.
combining actions and betsizes might make it difficult to understand the difference between betting and checking.
combing raise and bet actions might make it difficult to understand the difference between the two.

Question:
currently the state represents the state for the next palyer. When there is no next player e.g. board. Do we set pot odds, betsizes etc. to 0? As they cannot be calculated in relation to the next player.
Currently set to 0.

TODO:
fix issue where 3 handed and UTG no dealer

record player seats

Prompt for displaying 6 player games:

I am building a web server to display poker hands. There is a maximum of 6 players. I have an oval that represents the table, and would like to display the players around the table. Each player will have an associated position, stack, cards, indicator whether its their turn currently, and an optional display of a dealer button. This will be built in python with Flask. Lets first sketch out what is required in the HTML and CSS in a bulleted list.
