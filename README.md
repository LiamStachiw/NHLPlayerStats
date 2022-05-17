# NHLPlayerStats

This is meant to be an application used to find the best players in the NHL based on different aspects of the game. These stats are entirely made up and just for fun. Please don't take anything on the page seriously. The main intention of this app is to essentially act as a sandbox to mess around with python while using data that I find interesting. All stats are provided by MoneyPuck.com

## Defensive Skater Stats
Defensive score is calculated by using a combination of the player\'s on ice expected goals for %, shot attempts blocked %, on ice corsi %, % of penalties taken vs. drawn, % of takeaways vs. giveaways, defensive zone start %, a small factor of total hits as a factor of icetime, and their faceoff percentage (if they\'ve taken more than 25 faceoffs on the season). The stats used are averaged out, and multiplied by 10 to assign each player their defensive score.

Stats that are outside of the player's control (ie. penalties % and defensive zone start %) are also given a smaller weight towards the calculation of defensive score.

### No guarantees are made to the quality of the data. NHL data is known to have issues and biases.