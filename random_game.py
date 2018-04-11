from uno import UnoGame
import random
import operator

COLORS = ['red', 'yellow', 'green', 'blue']
ALL_COLORS = COLORS + ['black']
NUMBERS = list(range(10)) + list(range(1, 10))
SPECIAL_CARD_TYPES = ['skip', 'reverse', '+2']
COLOR_CARD_TYPES = NUMBERS + SPECIAL_CARD_TYPES * 2
BLACK_CARD_TYPES = ['wildcard', '+4']
CARD_TYPES = NUMBERS + SPECIAL_CARD_TYPES + BLACK_CARD_TYPES

SPECIAL_CARD_PRIORITY = ['+4', 'wildcard', '+2', 'skip', 'reverse']

# players = random.randint(2, 15)
players = 4
game = UnoGame(players)

print("Starting a {} player game".format(players))

choice_state = {'enemy_streak': {'color': None, 'num': 1},
                'enemy_out_of_cards': {'color': None, 0: False, 2: False}}

def update_state(player_id, last_card):
    if last_card.color == choice_state['enemy_streak']['color']:
        choice_state['enemy_streak']['num'] += 1
    else:
        choice_state['enemy_streak']['num'] = 1
        choice_state['enemy_streak']['color'] = last_card.color

def choose_card(player): 
    """
    Returns the index in the player's hand of the card he should play. Also returns new color of game
    """

    # Values to return
    best_card_index = None
    new_color = None

    player_id = player.player_id
    next_player = next(game._player_cycle)
    # print('next player: ', next_player, type(next_player))

    # Get list of player's action cards
    playable_action_cards = []
    playable_black_cards = []
    playable_special_cards = []
    playable_cards = []
    for card in player.hand:
        if game.current_card.playable(card):
            playable_cards.append(card)
        if card.card_type in BLACK_CARD_TYPES:
            playable_black_cards.append(card)
        elif card.card_type in SPECIAL_CARD_TYPES and game.current_card.playable(card):
            playable_special_cards.append(card)
    playable_action_cards = playable_black_cards + playable_special_cards

    # Get list of same number cards and same color cards
    same_number_cards = []
    same_color_cards = []
    for card in player.hand:
        if (card.card_type not in (SPECIAL_CARD_TYPES + BLACK_CARD_TYPES)) and card.card_type == game.current_card.card_type:
            same_number_cards.append(card)
        if (card.card_type not in BLACK_CARD_TYPES) and card.color == game.current_card.color:
            same_color_cards.append(card)

    print('Player id:', player_id)
    print('Player Hand:', player.hand)
    print('playable_action_cards:', playable_action_cards)

    # Get list of colors sorted by how common in team
    teammate = game.players[(player_id + 2) % 4]
    team_color_numbers = {'red': 0, 'blue': 0, 'yellow': 0, 'green': 0}
    for card in player.hand + teammate.hand:
        if card.color != 'black':
            team_color_numbers[card.color] += 1
    sorted_colors = [tup[0] for tup in sorted(team_color_numbers.items(), key=operator.itemgetter(1))]
    most_common_color = sorted_colors[-1]

    # Strategy 1 - if next player has <= 2 cards, play any action card if possible
    if len(next_player.hand) <= 2 and len(playable_action_cards) > 0:
        card_priorities = [(card, SPECIAL_CARD_PRIORITY.index(card.card_type)) for card in playable_action_cards]
        best_card = min(card_priorities, key = lambda t: t[1])[0]
        if best_card.card_type in BLACK_CARD_TYPES:
            new_color = most_common_color
        best_card_index = player.hand.index(best_card)

        return best_card_index, new_color

    # Strategy 2 - if enemy has played >= thres same color cards in a row, change color to another best possible color, using wildcard 
    #              if necessary
    thres = 5
    if choice_state['enemy_streak']['num'] >= thres:
        if len(same_number_cards) > 0: # We have a non-special playable card
            best_card = max(same_number_cards, key = lambda t: sorted_colors.index(t.color))
            best_card_index = player.hand.index(best_card)
            new_color = best_card.color
            return best_card_index, new_color
        elif len(playable_black_cards) > 0:
            best_card = max(playable_black_cards, key = lambda t: SPECIAL_CARD_PRIORITY.index(t.card_type))
            best_card_index = player.hand.index(best_card)
            new_color = most_common_color
            return best_card_index, new_color

    # Strategy 3 - if enemy had to draw card for a color, try to play that color
    if choice_state['enemy_out_of_cards'][0] or choice_state['enemy_out_of_cards'][2]:
        possible_cards = [card for card in player.hand if (game.current_card.playable(card) and card.color == choice_state['enemy_out_of_cards']['color'])]
        if len(possible_cards) > 0:
            done = False
            for card in possible_cards:
                if card.card_type not in SPECIAL_CARD_TYPES:
                    best_card_index = player.hand.index(card)
                    new_color = card.color
                    done = True
                    break
            if done == False:
                card = possible_cards[0]
                best_card_index = player.hand.index(card)
                new_color = card.color
            print(new_color)
            return best_card_index, new_color


    # Default strategy - play a random playable card
    for i, card in enumerate(player.hand):
        if game.current_card.playable(card):
            # Prefer not to play special cards 
            if card.card_type in SPECIAL_CARD_PRIORITY and (len(playable_cards) - len(playable_action_cards) > 0):
                continue
            if card.color == 'black':
                new_color = most_common_color
            best_card_index = player.hand.index(card)
            break

    return best_card_index, new_color

last_turn_new_color = None

count = 0
while game.is_active:
    count += 1
    player = game.current_player
    player_id = player.player_id
    # print(player.hand)
    if player.can_play(game.current_card):
        if player_id == 1 or player_id == 3: # Our bot
            card, new_color = choose_card(player)
            last_turn_new_color = new_color
            print("Player {} played {}".format(player, player.hand[card]))
            # print('New Color: ', new_color)
            game.play(player=player_id, card=card, new_color=new_color)
        else:
            for i, card in enumerate(player.hand):
                if game.current_card.playable(card):
                    if card.color == 'black':
                        new_color = random.choice(COLORS)
                    else:
                        new_color = None
                    print("Player {} played {}".format(player, card))

                    update_state(player_id, player.hand[i])
                    choice_state['enemy_out_of_cards'][player.player_id] = False # Related to strategy 3

                    game.play(player=player_id, card=i, new_color=new_color)
                    break
    else:
        # Related to Strategy 3
        if player.player_id == 0 or player.player_id == 2:
            if game.current_card.card_type != '+4':
                if game.current_card.card_type == 'wildcard':
                    choice_state['enemy_out_of_cards']['color'] = last_turn_new_color
                else:
                    choice_state['enemy_out_of_cards']['color'] = game.current_card.color
                choice_state['enemy_out_of_cards'][player.player_id] = True

        print("Player {} picked up".format(player))
        game.play(player=player_id, card=None)

print("{} player game - {} cards played".format(players, count))
