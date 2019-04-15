# -----------------------------------------------------------------------------------
# ---- Packages ---------------------------------------------------------------------
# -----------------------------------------------------------------------------------

# data handling
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
    draw_hands.append(draw_cards(decks = decks, draws = (players + 1) * 7, seed = seeds[i]))

# play through each hand using stand_strategies
blackjack_success = []
for i in range(hands):
    
    # get hand i and keep track of its drawing order
    table_hands = draw_hands[i]
    table_hands = table_hands.reset_index()
    
    # join face_values onto table_hands
    table_hands = pd.merge(face_values, table_hands, left_on = "Face", right_on = "Face", how = "right")
    
    # sort table_hands by index
    table_hands = table_hands.sort_values(by = "index", ascending = True).reset_index(drop = True)
    
    # remove the index column
    table_hands = table_hands.drop("index", axis = 1)
    
    # assign cards to players
    table_hands["Player"] = np.concatenate((np.tile(np.concatenate((["Player_" + str(i + 1) for i in range(players)], ["Dealer"])), 2),
                                            np.tile(["Unknown"], len(table_hands.index) - ((players + 1) * 2))))
    
    # create the order of Players
    player_order = np.concatenate((["Player_" + str(i + 1) for i in range(players)], ["Dealer"]))
    
    # split up table_hands by player_order
    player_hands = []
    for j in player_order:
        player_hands.append(table_hands.loc[table_hands["Player"] == j].reset_index(drop = True))
    
    # get the undealt cards
    undealt_cards = table_hands.loc[table_hands["Player"] == "Unknown"].reset_index(drop = True)
    
    
    
    






# draw cards for each hand
set.seed(42)
draw_hands = lapply(1:hands, function(i) draw_cards(decks = decks, draws = (players + 1) * 7))

# setup a cluster for parallel processing
# workers = getDTthreads() - 1
# cl = makeCluster(workers, type = "SOCK", outfile = "")
# registerDoSNOW(cl)

# play through each hand
# blackjack_success = foreach(i = 1:length(draw_hands)) %dopar%
blackjack_success = lapply(1:length(draw_hands), function(i)
{
  require(data.table)
  
  # get hand i and keep track of its drawing order
  table_hands = data.table(draw_hands[[i]])
  table_hands[, index := 1:nrow(table_hands)]
  
  # join card_values onto table_hands
  setkey(table_hands, Card)
  setkey(card_values, Card)
  table_hands = card_values[table_hands]
  table_hands = table_hands[order(index)]
  table_hands[, index := NULL]
  
  # assign cards to players
  table_hands[, Player := c(rep(c(paste0("Player_", 1:players), "Dealer"), 2), rep("Unknown", nrow(table_hands) - ((players + 1) * 2)))]
  
  # create the order of Players
  player_order = c(paste0("Player_", 1:players), "Dealer")
  
  # split up table_hands by player_order
  player_hands = lapply(player_order, function(p) data.table(table_hands[Player == p]))
  
  # get the undealt cards
  undealt_cards = data.table(table_hands[Player == "Unknown"])
  
  # play through each strategy on hand i
  strategy_success = unlist(lapply(1:nrow(stand_strategies), function(k)
  {
    # set up an empty vector to store hand values for strategy k
    hand_values = c()
    
    # play through strategy k for each player
    for(j in 1:length(player_hands))
    {
      # get player j's hand
      player_hand = data.table(player_hands[[j]])
      
      # get the value of player j's hand
      hand_value = sum(player_hand$Value)
      
      # get the value of player j's k-th stand_strategy
      stand_value = unname(unlist(stand_strategies[k, j, with = FALSE]))
      
      # draw another card while hand_value is less than stand_value
      while(hand_value < stand_value)
      {
        # add a card to player_hand
        player_hand = rbind(player_hand, undealt_cards[1])
        
        # remove a card from undealt_cards
        undealt_cards = undealt_cards[-1]
        
        # update hand_value
        hand_value = sum(player_hand$Value)
        
        # if the hand_value broke 21 and there's an Ace in the hand, update the Ace value to 1
        if(hand_value > 21 & "Ace" %in% player_hand$Card)
        {
          # update the value of Ace
          player_hand[Card == "Ace", Value := 1]
          
          # update hand_value
          hand_value = sum(player_hand$Value)
        }
      }
      
      # add hand_value to hand_values
      hand_values = append(hand_values, hand_value)
    }
    
    # determine the table win percentage for strategy k on hand i
    win_percent = sum(unlist(lapply(1:players, function(m)
      ifelse(hand_values[players + 1] > 21 & hand_values[m] <= 21, 1, 
             ifelse(hand_values[m] > hand_values[players + 1] & hand_values[m] <= 21, 1, 0))))) / players
    
    return(win_percent)
  }))
  
  # make strategy_success into a table
  strategy_success = cbind(data.table(Hand = i, Strategy = 1:length(strategy_success), Success = strategy_success), stand_strategies)
  
  # print out completion of hand i
  cat("----", as.character(nrow(stand_strategies)), "strategies on hand", i, "of", as.character(length(draw_hands)), "evaluated at", as.character(Sys.time()), "----\n")
  
  return(strategy_success)
})

# end the cluster
# stopCluster(cl)

# combine the list of tables into one table
blackjack_success = rbindlist(blackjack_success)

# average the success of each strategy
strategy_score = data.table(blackjack_success[, .(Success = mean(Success)), by = .(Strategy)])

# rank the success of each strategy
strategy_score = strategy_score[order(Success, decreasing = TRUE)]

# get the average stand value
strategy_score[, Stand_Avg := rowSums(stand_strategies[strategy_score$Strategy, 1:players, with = FALSE]) / players]

# add the player stand values to strategy_score
strategy_score = cbind(strategy_score, stand_strategies[strategy_score$Strategy, 1:players, with = FALSE])

# see if there is a linear relationship between stand strategy and success
cor(strategy_score$Success, strategy_score$Stand_Avg)
cor(strategy_score$Success, strategy_score$Player_1)
cor(strategy_score$Success, strategy_score$Player_2)
cor(strategy_score$Success, strategy_score$Player_3)
cor(strategy_score$Success, strategy_score$Player_4)
strategy_score

















