# -*- coding: utf-8 -*-
"""
Simulating with Dice

@author: Nick
"""

from copy import deepcopy
import numpy as np
import pandas as pd

def roll(n):
    """
    Represents rolling dice

    Parameters
    ----------
    n : int
        The number of dice to roll.

    Returns
    -------
    roll_ : list
        The number rolled for each die.
    """
    roll_ = []
    for i in range(n):
        roll_.append(np.random.choice(np.arange(6) + 1, size=1)[0])
    return roll_

def sublist(list_one, list_two, diff=False):
    """
    Checks if each element in list_one is within list_two
    Alternatively substracts lists: list_two - list_one

    Parameters
    ----------
    list_one : list
        list of values.

    list_two : list
        list of values.

    diff : bool
        Should the difference between lists be returned?

    Returns
    -------
    out : bool, list
        DESCRIPTION.
    """
    list_two = deepcopy(list_two)
    count=0
    for i in list_one:
        if i in list_two:
            count += 1
            list_two.remove(i)

        if count==len(list_one):
            if diff:
                return list_two
            return True
    if diff:
        return list_two
    return False


def value(a):
    """
    Determines the value(s) of a roll of the dice

    Parameters
    ----------
    a : list
        A roll of the dice.

    Returns
    -------
    values_ : dictionary
        Indicating the value of a roll and the number of dice left
    """
    # build a table of all values
    roll_ = [[5], [1], [1, 1, 1], [2, 2, 2], [3, 3, 3],
             [4, 4, 4], [5, 5, 5], [6, 6, 6], [1, 1, 1, 1], [2, 2, 2, 2],
             [3, 3, 3, 3], [4, 4, 4, 4], [5, 5, 5, 5], [6, 6, 6, 6], [1, 1, 1, 1, 1],
             [2, 2, 2, 2, 2], [3, 3, 3, 3, 3], [4, 4, 4, 4, 4], [5, 5, 5, 5, 5], [6, 6, 6, 6, 6],
             [1, 1, 1, 1, 1, 1], [2, 2, 2, 2, 2, 2], [3, 3, 3, 3, 3, 3], [4, 4, 4, 4, 4, 4], [5, 5, 5, 5, 5, 5],
             [6, 6, 6, 6, 6, 6], [1, 2, 3, 4, 5, 6]]
    value_ = [50, 100, 1000, 200, 300,
              400, 500, 600, 2000, 400,
              600, 800, 1000, 1200, 3000,
              600, 900, 1200, 1500, 1800,
              4000, 800, 1200, 1600, 2000,
              2400, 1000]

    match_ = []
    for r in roll_:
        match_.append(sublist(r, a))

    values_ = pd.DataFrame({"roll": roll_,
                            "value": value_,
                            "match": match_})

    # sort the table and only keep the matches
    values_ = values_.sort_values(by="value")
    values_ = values_.loc[values_["match"] == True].reset_index(drop=True)

    # find how many points the roll is worth
    # find how many dice are left
    if values_.shape[0] == 0:
        points = 0
        left = len(a)
    else:
        points = values_["value"].tolist()[-1]
        left = len(a) - len(values_["roll"].tolist()[-1])

    return {"points": points, "dice": left}

def play(rounds=10, min_pts=300, min_dice=3):
    """
    Play a game of dice

    Parameters
    ----------
    rounds : int
        The number of rounds in the game
        
    min_pts : int
        The minium number of points to stop rolling in a round
        
    min_dice : int
        The minimum number of dice to keep rolling in a round

    Returns
    -------
    score : pandas DataFrame
        The score after each round

    """
    score = pd.DataFrame()
    r=1
    while r <= rounds:
        pts=0
        dice=6
        rolling=True
        while rolling:
            roll_ = roll(dice)
            value_ = value(roll_)
            pts = pts + value_["points"]
            dice = value_["dice"]
            
            # reset the dice
            if dice == 0:
                dice = 6

            # got nothing on the roll
            if value_["points"] == 0:
                pts = 0
                rolling = False

            # met desired min points for this round
            if pts >= min_pts:
                rolling = False

            # no longer have enough dice to roll
            if dice < min_dice:
                rolling = False
        score = pd.concat([score, pd.DataFrame({"Round": [r], "Points": [pts]})], axis=0)
        r += 1
    score["Total"] = score["Points"].cumsum().reset_index(drop=True)
    return score

# set up grid for rolling dice
min_pts = [100, 200, 300, 400, 500, 600]
min_dice = [1, 2, 3]
grid = pd.DataFrame(np.array(np.meshgrid(min_pts, min_dice)).reshape(2, int(len(min_pts) * len(min_dice))).T,
                    columns = ["min_pts", "min_dice"])

# score each strategy in the grid with a game of dice
score = []
for i in range(grid.shape[0]):
    play_i = play(rounds=500, min_pts=grid["min_pts"].tolist()[i], min_dice=grid["min_dice"].tolist()[i])
    score.append(play_i["Total"].tolist()[-1])
grid["score"] = score
grid.sort_values(by="score", ascending=False)
