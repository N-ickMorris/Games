# open up a graphics window
windows()

# ----------------------------------------------------------------------------------
# ---- Packages --------------------------------------------------------------------
# ----------------------------------------------------------------------------------

require(ggplot2)
require(scales)
require(stringr)
require(data.table)
require(foreach)
require(doSNOW)

# ----------------------------------------------------------------------------------
# ---- Functions -------------------------------------------------------------------
# ----------------------------------------------------------------------------------

# build a function for rolling dice
roll_dice = function(rolls = 1000, dice = 2, sides = 6, seed = NULL)
{
  require(data.table)
  
  if(!is.null(seed)) set.seed(seed)
  results = data.table(t(sapply(1:rolls, function(i) sample(x = 1:sides, size = dice, replace = TRUE))))
  setnames(results, paste0("Dice_", 1:ncol(results)))
  
  return(results)
}

# build a function for drawing cards
draw_cards = function(decks = 1, draws = 18, seed = NULL)
{
  require(data.table)
  require(stringr)
  
  cards = unlist(lapply(c("Hearts", "Diamonds", "Spades", "Clubs"), function(i) paste(c(2:10, "Jack", "King", "Queen", "Ace"), i, sep = "_")))
  
  if(!is.null(seed)) set.seed(seed)
  drawing = sample(x = rep(cards, decks), size = draws, replace = FALSE)
  
  drawing = data.table(str_split_fixed(string = drawing, pattern = "_", n = 2))
  setnames(drawing, c("Card", "Suite"))
  
  return(drawing)
}

# build a function for spinning roulette
spin_roulette = function(spins = 1000, seed = NULL)
{
  require(data.table)
  
  values = data.table(Number = c("00", as.character(0:36)),
                      First_12 = c(rep("No", 2), rep("Yes", 12), rep("No", 24)),
                      Second_12 = c(rep("No", 14), rep("Yes", 12), rep("No", 12)),
                      Third_12 = c(rep("No", 26), rep("Yes", 12)),
                      First_18 = c(rep("No", 2), rep("Yes", 18), rep("No", 18)),
                      Second_18 = c(rep("No", 20), rep("Yes", 18)),
                      Even = c(rep("No", 2), rep(c("No", "Yes"), 18)),
                      Odd = c(rep("No", 2), rep(c("Yes", "No"), 18)),
                      Green = c(rep("Yes", 2), rep("No", 36)),
                      Red = c(rep("No", 2), rep(c(rep(c("Yes", "No"), 5)[-10], c("No", "No", "Yes", "No", "Yes", "No", "Yes", "No", "Yes")), 2)))
  
  values[, Black := ifelse(Red == "Yes", "No", ifelse(Green == "Yes", "No", "Yes"))]
  values[, Min_2to1 := c(rep("No", 2), rep(c("Yes", "No", "No"), 12))]
  values[, Mid_2to1 := c(rep("No", 2), rep(c("No", "Yes", "No"), 12))]
  values[, Max_2to1 := c(rep("No", 2), rep(c("No", "No", "Yes"), 12))]
  
  if(!is.null(seed)) set.seed(seed)
  turns = sample(x = 1:nrow(values), size = spins, replace = TRUE)
  
  return(values[turns])
}

# check out the output of each function
roll_dice()
draw_cards()
spin_roulette()

# ----------------------------------------------------------------------------------
# ---- Rolling Dice ----------------------------------------------------------------
# ----------------------------------------------------------------------------------

# roll a pair of dice
dice = roll_dice(rolls = 3e5, dice = 2, sides = 6, seed = 21)

# compute the total of each roll, and the combination of each roll
dice[, Total := rowSums(dice)]
dice[, Combo := paste0(ifelse(Dice_1 < Dice_2, Dice_1, Dice_2), ",", ifelse(Dice_1 > Dice_2, Dice_1, Dice_2))]

# plot the distribution of the dice roll total
plot_total = ggplot(data = dice, aes(x = Total)) + 
  geom_histogram(fill = "cornflowerblue", color = "white", binwidth = 1) + 
  scale_x_continuous(breaks = sort(unique(dice$Total))) + 
  scale_y_continuous(label = comma) + 
  ggtitle("Rolling Two Dice") + 
  labs(x = "Total", y = "Frequency") + 
  theme_bw(base_size = 25) +
  theme(legend.position = "none", 
        legend.key.size = unit(.25, "in"),
        plot.title = element_text(hjust = 0.5),
        # axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank()) +
  guides(color = guide_legend(override.aes = list(size = 10, linetype = 1, alpha = 1), nrow = 1, byrow = TRUE))

plot_total

# plot the distribution of the dice roll combination
plot_combo = ggplot(data = dice, aes(x = as.factor(Combo))) + 
  geom_bar(fill = "cornflowerblue", color = "white") + 
  scale_y_continuous(label = comma) + 
  ggtitle("Rolling Two Dice") + 
  labs(x = "Combination", y = "Frequency") + 
  theme_bw(base_size = 25) +
  theme(legend.position = "none", 
        legend.key.size = unit(.25, "in"),
        plot.title = element_text(hjust = 0.5),
        # axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank()) +
  guides(color = guide_legend(override.aes = list(size = 10, linetype = 1, alpha = 1), nrow = 1, byrow = TRUE))

plot_combo

# ----------------------------------------------------------------------------------
# ---- Blackjack -------------------------------------------------------------------
# ----------------------------------------------------------------------------------

# blackjack rules: https://www.wikihow.com/Play-Blackjack

# how many players are there?
players = 4

# what are the values for players standing?
player_stands = 12:17

# what is the value for the dealer standing?
dealer_stands = 17

# how many hands will be played?
hands = 100

# how many decks will be used?
decks = 2

# create standing strategies
stand_strategies = data.table(expand.grid(append(lapply(1:players, function(i) player_stands), list(dealer_stands))))

# update the column names for stand_strategies
setnames(stand_strategies, c(paste0("Player_", 1:players), "Dealer"))

# create a table of values for each card
card_values = data.table(Card = c(2:10, "Jack", "Queen", "King", "Ace"), 
                         Value = c(2:10, 10, 10, 10, 11))

# draw cards for each hand
set.seed(42)
draw_hands = lapply(1:hands, function(i) draw_cards(decks = decks, draws = 52 * decks))

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

# ----------------------------------------------------------------------------------
# ---- Craps -----------------------------------------------------------------------
# ----------------------------------------------------------------------------------

# craps rules: https://www.wikihow.com/Play-Craps




# ----------------------------------------------------------------------------------
# ---- Roulette --------------------------------------------------------------------
# ----------------------------------------------------------------------------------

# roulette rules: https://www.wikihow.com/Play-Roulette




# ----------------------------------------------------------------------------------
# ---- 5-Card Poker ----------------------------------------------------------------
# ----------------------------------------------------------------------------------

# 5-card poker rules: https://www.wikihow.com/Play-Five-Card-Draw










