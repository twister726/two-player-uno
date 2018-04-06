from uno import UnoGame
import random

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
    for card in player.hand:
        if card.card_type in BLACK_CARD_TYPES:
            playable_action_cards.append(card)
        elif card.card_type in SPECIAL_CARD_TYPES and game.current_card.playable(card):
            playable_action_cards.append(card)

    print('Player id:', player_id)
    print('Player Hand:', player.hand)
    print('playable_action_cards:', playable_action_cards)

    # Get most common color in team
    teammate = game.players[(player_id + 2) % 4]
    team_color_numbers = {'red': 0, 'blue': 0, 'yellow': 0, 'green': 0}
    for card in player.hand + teammate.hand:
        if card.color != 'black':
            team_color_numbers[card.color] += 1
    most_common_color = max(team_color_numbers, key=team_color_numbers.get)

    # Strategy 1 - if next player has <= 2 cards, play any action card if possible
    if len(next_player.hand) <= 2 and len(playable_action_cards) > 0:
        card_priorities = [(card, SPECIAL_CARD_PRIORITY.index(card.card_type)) for card in playable_action_cards]
        best_card = min(card_priorities, key = lambda t: t[1])[0]
        if best_card.card_type in BLACK_CARD_TYPES:
            new_color = most_common_color
        best_card_index = player.hand.index(best_card)

    # Default strategy - play a random playable card
    for i, card in enumerate(player.hand):
        if game.current_card.playable(card):
            if card.color == 'black':
                new_color = random.choice(COLORS)
            best_card_index = player.hand.index(card)
            break

    return best_card_index, new_color

count = 0
while game.is_active:
    count += 1
    player = game.current_player
    player_id = player.player_id
    # print(player.hand)
    if player.can_play(game.current_card):
        if player_id == 1 or player_id == 3: # Our bot
            card, new_color = choose_card(player)
            print("Player {} played {}".format(player, player.hand[card]))
            game.play(player=player_id, card=card, new_color=new_color)
        else:
            for i, card in enumerate(player.hand):
                if game.current_card.playable(card):
                    if card.color == 'black':
                        new_color = random.choice(COLORS)
                    else:
                        new_color = None
                    print("Player {} played {}".format(player, card))
                    game.play(player=player_id, card=i, new_color=new_color)
                    break
    else:
        print("Player {} picked up".format(player))
        game.play(player=player_id, card=None)

print("{} player game - {} cards played".format(players, count))
