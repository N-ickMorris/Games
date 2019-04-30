# set the path of where the input files are
mywd = "C:\\Users\\Nick Morris\\Desktop"

# -----------------------------------------------------------------------------------
# ---- Packages ---------------------------------------------------------------------
# -----------------------------------------------------------------------------------

# data handling
import os
import pandas as pd
import numpy as np
import gc
import time

# graphics
from plotnine import *

# ----------------------------------------------------------------------------------
# ---- Functions -------------------------------------------------------------------
# ----------------------------------------------------------------------------------

# build a function for rolling dice
def roll_dice(rolls = 100, dice = 2, sides = 6, seed = None):
    
    # set the seed
    np.random.seed(seed)
    
    # roll the dice
    dice_rolls = pd.DataFrame(np.random.choice(a = [i + 1 for i in range(sides)],
                                               size = (rolls, dice),
                                               replace = True),
                              columns = ["Dice_" + str(i + 1) for i in range(dice)])
    return dice_rolls

# build a function for drawing cards
def draw_cards(decks = 1, draws = 18, seed = None):
    
    # set up all the suites
    suites = ["Hearts", "Diamonds", "Spades", "Clubs"]
    
    # set up all the face values
    faces = [i + 2 for i in range(9)]
    faces.extend(["Jack", "King", "Queen", "Ace"])
    
    # assign each face value to each suite
    cards = [str(j) + "_" + i for j in faces for i in suites]
    
    # set the seed
    np.random.seed(seed)
    
    # create decks of cards and shuffle them
    cards = np.random.permutation(np.repeat(cards, decks))
    
    # draw the cards
    drawing = pd.Series([cards[i] for i in np.random.choice(a = range(len(cards)),
                                                            size = (min(draws, len(cards))),
                                                            replace = False)])
    
    # split up the cards by their face value and suite
    drawing = drawing.str.split("_", expand = True)
    
    # update the column names in drawing
    drawing.columns = ["Face", "Suite"]
    
    return drawing

# build a function for spinning roulette
def spin_roulette(spins = 100, seed = None):
    
    # set up all the numbers
    Number = np.append(["00"], [str(i) for i in range(37)])
    
    # determine which numbers are the first 12
    First_12 = np.concatenate((np.repeat("No", 2), np.repeat("Yes", 12), np.repeat("No", 24)))
    
    # determine which numbers are the second 12
    Second_12 = np.concatenate((np.repeat("No", 14), np.repeat("Yes", 12), np.repeat("No", 12)))
    
    # determine which numbers are the third 12
    Third_12 = np.concatenate((np.repeat("No", 26), np.repeat("Yes", 12)))
    
    # determine which numbers are the first 18
    First_18 = np.concatenate((np.repeat("No", 2), np.repeat("Yes", 18), np.repeat("No", 18)))
    
    # determine which numbers are the second 18
    Second_18 = np.concatenate((np.repeat("No", 20), np.repeat("Yes", 18)))
    
    # determine which numbers are even
    Even = np.concatenate((np.repeat("No", 2), np.tile(["No", "Yes"], 18)))
    
    # determine which numbers are odd
    Odd = np.concatenate((np.repeat("No", 2), np.tile(["Yes", "No"], 18)))
    
    # determine which numbers are green
    Green = np.concatenate((np.repeat("Yes", 2), np.repeat("No", 36)))
    
    # determine which numbers are red
    Red = np.concatenate((np.repeat("No", 2), np.tile(np.append(np.tile(["Yes", "No"], 5)[:-1], ["No", "No", "Yes", "No", "Yes", "No", "Yes", "No", "Yes"]), 2)))
    
    # determine which numbers are black
    Black = ["Yes" if i == "No" else "No" for i in Red]
    Black[:2] = ["No", "No"]
    Black = np.array(Black)
    
    # determine which numbers are low 2 to 1
    Low_2to1 = np.concatenate((np.repeat("No", 2), np.tile(["Yes", "No", "Yes"], 12)))
    
    # determine which numbers are middle 2 to 1
    Middle_2to1 = np.concatenate((np.repeat("No", 2), np.tile(["No", "Yes", "No"], 12)))
    
    # determine which numbers are high 2 to 1
    High_2to1 = np.concatenate((np.repeat("No", 2), np.tile(["No", "No", "Yes"], 12)))
    
    # create the roulette values
    roulette = pd.DataFrame({"Number": Number,
                             "First_12": First_12,
                             "Second_12": Second_12,
                             "Third_12": Third_12,
                             "First_18": First_18,
                             "Second_18": Second_18,
                             "Even": Even,
                             "Odd": Odd,
                             "Green": Green,
                             "Red": Red,
                             "Black": Black,
                             "Low_2to1": Low_2to1,
                             "Middle_2to1": Middle_2to1,
                             "High_2to1": High_2to1})
    
    # spin values from roulette 
    values = roulette.sample(n = spins, axis = 0, replace = True, random_state = seed).reset_index(drop = True)
    
    return values

# check out the output of each function
roll_dice()
draw_cards()
spin_roulette()

# ----------------------------------------------------------------------------------
# ---- Rolling Dice ----------------------------------------------------------------
# ----------------------------------------------------------------------------------

# set the work directory
os.chdir(mywd)

# roll a pair of dice
dice = roll_dice(rolls = int(3e5), dice = 2, sides = 6, seed = 21)

# compute the total of each roll
dice["Total"] = dice.sum(axis = 1)

# compute the combination of each roll
dice["Combo"] = dice[["Dice_1", "Dice_2"]].values.tolist()

# sort each roll combination
dice["Combo"] = dice["Combo"].apply(sorted)

# make Combo categorical
dice["Combo"] = pd.Categorical(values = dice["Combo"].astype("str"))

# plot the distribution of the dice roll total
total_plot = (ggplot(dice, aes(x = "Total")) +
  geom_histogram(fill = "cornflowerblue", color = "white", binwidth = 1) + 
  scale_x_continuous(breaks = tuple(set(dice["Total"]))) + 
  scale_y_continuous(labels = lambda l: [format(int(np.round(v, 0)), ",") for v in l]) +
  ggtitle("Rolling Two Dice\n") +
  labs(x = "Total", y = "Frequency") +
  theme_bw(25) +
  theme(plot_title = element_text(hjust = 0.5, vjust = 1),
        figure_size = (14, 10),
        aspect_ratio = 4/5,
        panel_grid_major = element_blank(),
        panel_grid_minor = element_blank()))

total_plot

# plot the distribution of the dice roll combination
combo_plot = (ggplot(dice, aes(x = "Combo")) +
  geom_bar(fill = "cornflowerblue", color = "white") + 
  scale_y_continuous(labels = lambda l: [format(int(np.round(v, 0)), ",") for v in l]) +
  ggtitle("Rolling Two Dice\n") +
  labs(x = "Combination", y = "Frequency") +
  theme_bw(25) +
  theme(plot_title = element_text(hjust = 0.5, vjust = 1),
        figure_size = (14, 10),
        aspect_ratio = 4/5,
        axis_text_x = element_text(angle = 45, hjust = 0.5, vjust = 1),
        panel_grid_major = element_blank(),
        panel_grid_minor = element_blank()))

combo_plot

# ----------------------------------------------------------------------------------
# ---- Blackjack -------------------------------------------------------------------
# ----------------------------------------------------------------------------------

# blackjack rules: https://www.wikihow.com/Play-Blackjack

# how many players are there?
players = 5

# what are the values for players standing?
player_stands = [i for i in range(12, 17)]

# what is the value for the dealer standing?
dealer_stands = [17]

# how many hands will be played?
hands = 1000

# how many decks will be used?
decks = 7

# set up a grid for standing strategies
stand_strategies = pd.DataFrame(np.array(np.meshgrid(player_stands,
                                                     player_stands,
                                                     player_stands,
                                                     player_stands,
                                                     player_stands,
                                                     dealer_stands)).reshape(players + 1, int(len(player_stands)**players * len(dealer_stands))).T,
                                columns = np.concatenate((["Player_" + str(i + 1) for i in range(players)], ["Dealer"])))

# add a Strategy column to stand_strategies
stand_strategies["Strategy"] = stand_strategies.index.values

# set up all the face values
faces = [str(i + 2) for i in range(9)]
faces.extend(["Jack", "King", "Queen", "Ace"])

# set up all the point values for each face
points = [i + 2 for i in range(9)]
points.extend([10, 10, 10, 11])

# create a table of face values
face_values = pd.DataFrame({"Face": faces, "Value": points})

# draw cards for each hand
draw_hands = []
np.random.seed(42)
seeds = np.random.choice(a = [i + 1 for i in range(int(hands * 100))],
                         size = (hands),
                         replace = False)
for i in range(hands):
    draw_hands.append(draw_cards(decks = decks, draws = (players + 1) * (2 + 4), seed = seeds[i]))

# create the order of Players
player_order = np.concatenate((["Player_" + str(o + 1) for o in range(players)], ["Dealer"]))

# set up a table to hold the strategy success
blackjack_success = pd.DataFrame(columns = np.append(["Hand", "Strategy"], [w + "_won" for w in player_order[:-1]]))

# play through each hand using stand_strategies
for i in range(214, hands):
    
    # play through each strategy on hand i
    for k in stand_strategies.index.values:
        
        # get hand i and keep track of its drawing order
        table_hands = draw_hands[i]
        table_hands = table_hands.reset_index()
        
        # join face_values onto table_hands
        table_hands = pd.merge(face_values, table_hands, left_on = "Face", right_on = "Face", how = "right")
        
        # sort table_hands by index
        table_hands = table_hands.sort_values(by = "index", ascending = True).reset_index(drop = True)
        
        # remove the index column
        table_hands = table_hands.drop("index", axis = 1)
        
        # deal cards to players
        table_hands["Player"] = np.concatenate((np.tile(np.concatenate((["Player_" + str(d + 1) for d in range(players)], ["Dealer"])), 2),
                                                np.tile(["Unknown"], len(table_hands.index) - ((players + 1) * 2))))
        
        # split up table_hands by player_order
        player_hands = []
        for j in player_order:
            player_hands.append(table_hands.loc[table_hands["Player"] == j].reset_index(drop = True))
        
        # get the undealt cards
        undealt_cards = table_hands.loc[table_hands["Player"] == "Unknown"].reset_index(drop = True)
        
        # set up a list to hold the final value of each players hand
        hand_values = []
        
        # play through strategy k for each player
        for p in range(len(player_order)):
            
            # get player p's hand
            player_hand = player_hands[p]
            
            # get the value of player p's hand
            hand_value = sum(player_hand["Value"])
            
            # get the value of player p's k-th stand_strategy
            stand_value = stand_strategies[player_order[p]][k]
            
            # draw another card while hand_value is less than stand_value
            while hand_value < stand_value:
                
                # add a card to player_hand
                player_hand = pd.concat([player_hand, undealt_cards.head(1)], axis = "rows").reset_index(drop = True)
                
                # remove this card from undealt_cards
                undealt_cards = undealt_cards.iloc[1:].reset_index(drop = True)
                
                # get the value of player p's hand
                hand_value = sum(player_hand["Value"])
                
                # if hand_value > 21 and there's an Ace in player_hand, update the Ace value to 1
                if (hand_value > 21 and "Ace" in player_hand["Face"]):
                    
                    # determine where the Ace is
                    ace_position = np.where(np.array(player_hand["Face"]) == "Ace")[0].astype("int")
                    
                    # update the Ace value(s)
                    for a in ace_position:
                        player_hand.at[ace_position[a], "Value"] = 1
                    
                    # get the value of player p's hand
                    hand_value = sum(player_hand["Value"])
                    
            # add hand_value to hand_values
            hand_values = np.append(hand_values, hand_value)
        
        # set up a list for holding strategy success
        strategy_success = [i, k]
        
        # determine the table results for strategy k on hand i
        for r in range(players):
            
            # if the dealer broke 21 and player r didn't, that's a win
            if (hand_values[players] > 21 and hand_values[r] <= 21):
                strategy_success = np.append(strategy_success, [1])
            
            # if player r beat the dealer without breaking 21, that's a win
            elif (hand_values[r] > hand_values[players] and hand_values[r] <= 21):
                strategy_success = np.append(strategy_success, [1])
            
            # otherwise player r lost
            else:
                strategy_success = np.append(strategy_success, [0])
        
        # convert strategy_success into a table
        strategy_success_table = pd.DataFrame(columns = blackjack_success.columns)
        strategy_success_table.loc[0] = strategy_success
        
        # add strategy_success_table to blackjack_success
        blackjack_success = pd.concat([blackjack_success, strategy_success_table], axis = "rows").reset_index(drop = True)
        
        # clean out the garbage in RAM
        gc.collect()
        
        # report progress
        print("---- Blackjack Strategy " + str(k + 1) + " of " + str(len(stand_strategies.index.values)) + " on Hand " + str(i + 1) + " of " + str(hands) + " completed on " + time.ctime() + " ----")

# export the results
# blackjack_success.to_csv("Blackjack Simulation - Part 3.csv", index = False)

# import the results
# blackjack_success1 = pd.read_csv("Blackjack Simulation - Part 1.csv")
# blackjack_success2 = pd.read_csv("Blackjack Simulation - Part 2.csv")
# blackjack_success = pd.concat([blackjack_success1, blackjack_success2], axis = "index").reset_index(drop = True)

# compute the starting value of each players hand
start_values = pd.DataFrame(columns = np.append(["Hand"], [h + "_hand" for h in player_order[:-1]]))
for i in range(hands):
    
    # get hand i and keep track of its drawing order
    hand_i = draw_hands[i]
    hand_i = hand_i.reset_index()
    
    # join face_values onto hand_i
    hand_i = pd.merge(face_values, hand_i, left_on = "Face", right_on = "Face", how = "right")
    
    # sort hand_i by index
    hand_i = hand_i.sort_values(by = "index", ascending = True).reset_index(drop = True)
    
    # remove the index column
    hand_i = hand_i.drop("index", axis = 1)
    
    # deal cards to players
    hand_i["Player"] = np.concatenate((np.tile(np.concatenate((["Player_" + str(d + 1) for d in range(players)], ["Dealer"])), 2),
                                            np.tile(["Unknown"], len(hand_i.index) - ((players + 1) * 2))))
    
    # compute the starting value of hand_i for each player
    hand_i_values = [i]
    for j in player_order[:-1]:
        hand_i_values = np.append(hand_i_values, sum(hand_i.loc[hand_i["Player"] == j]["Value"]))
    
    # store hand_i_values
    start_values.loc[i] = hand_i_values

# compute the average table strategy
stand_strategies["Table"] = np.round(stand_strategies[player_order[:-1]].apply(np.mean, axis = 1), 1)

# compute the table win percentage
blackjack_success["Table_won"] = np.divide(blackjack_success[[w + "_won" for w in player_order[:-1]]].apply(np.sum, axis = 1), len(player_order[:-1]))

# create an index column in blackjack_success
blackjack_success = blackjack_success.reset_index()

# join stand_strategies onto blackjack_success
blackjack_success = pd.merge(stand_strategies, blackjack_success, left_on = "Strategy", right_on = "Strategy", how = "right")

# join start_values onto blackjack_success
blackjack_success = pd.merge(start_values, blackjack_success, left_on = "Hand", right_on = "Hand", how = "right")

# sort blackjack_success by index
blackjack_success = blackjack_success.sort_values(by = "index", ascending = True).reset_index(drop = True)

# remove the index column
blackjack_success = blackjack_success.drop("index", axis = "columns")

# compute the win percentage for each strategy of each player
strategy_score = []
for i in range(len(player_order) - 1):
    if i == 0:
        strategy_score.append(blackjack_success.groupby(player_order[i]).mean()[[player_order[i] + "_won"]].rename_axis("Player").reset_index())
    else:
        strategy_score.append(pd.concat([strategy_score[i - 1], blackjack_success.groupby(player_order[i]).mean()[[player_order[i] + "_won"]].reset_index(drop = True)], axis = "columns"))

# update strategy_score
strategy_score = strategy_score[len(player_order) - 2]

# compute the average strategy_score
strategy_score["Avg_won"] = strategy_score[[w + "_won" for w in player_order[:-1]]].apply(np.mean, axis = 1)

# sort strategy_score by Avg_won
strategy_score = strategy_score.sort_values(by = "Avg_won", ascending = False).reset_index(drop = True)

# compute the average table score
table_score = blackjack_success.groupby("Table").mean()["Table_won"].reset_index()

# sort table_score by Table_won
table_score = table_score.sort_values(by = "Table_won", ascending = False).reset_index(drop = True)

# compute the win percentage for each strategy of each player
strategy_hand_score = []
for i in range(len(player_order) - 1):
    if i == 0:
        strategy_hand_score.append(blackjack_success.groupby([player_order[i], player_order[i] + "_hand"]).mean()[[player_order[i] + "_won"]].rename_axis(["Player", "Player_hand"]).reset_index())
    else:
        strategy_hand_score.append(pd.concat([strategy_hand_score[i - 1], blackjack_success.groupby([player_order[i], player_order[i] + "_hand"]).mean()[[player_order[i] + "_won"]].reset_index(drop = True)], axis = "columns"))

# update strategy_hand_score
strategy_hand_score = strategy_hand_score[len(player_order) - 2]

# compute the average strategy_score
strategy_hand_score["Avg_won"] = strategy_hand_score[[w + "_won" for w in player_order[:-1]]].apply(np.mean, axis = 1)

# sort strategy_hand_score by Avg_won
strategy_hand_score = strategy_hand_score.sort_values(by = ["Avg_won", "Player"], ascending = False).reset_index(drop = True)

# get the best strategy for each starting hand value
hand_scores = pd.DataFrame(columns = strategy_hand_score.columns)
for i in list(set(strategy_hand_score["Player_hand"])):
    
    # get the scores for starting hand i
    hand_score_i = strategy_hand_score.loc[strategy_hand_score["Player_hand"] == i]
    
    # keep the max value(s) of Avg_won
    hand_score_i = hand_score_i.loc[hand_score_i["Avg_won"] == max(hand_score_i["Avg_won"])]
    
    # sort hand_score_i by Player and take the first row
    hand_score_i = hand_score_i.sort_values(by = "Player", ascending = True).reset_index(drop = True).head(1)
    
    # add hand_score_i to hand_scores
    hand_scores = pd.concat([hand_scores, hand_score_i], axis = "index").reset_index(drop = True)

# only keep hand values up to 21
hand_scores = hand_scores.loc[hand_scores["Player_hand"] <= 21]

# sort hand_scores by Player and Player_hand
hand_scores = hand_scores.sort_values(by = ["Player", "Player_hand"], ascending = True).reset_index(drop = True)

# write out hand_scores
hand_scores.to_csv("Blackjack Strategy.csv", index = False)











