from __future__ import print_function
import sys, random
from time import sleep
from sys import stdin, exit
from PodSixNet.Connection import connection, ConnectionListener

# This example uses Python threads to manage async input from sys.stdin.
# This is so that I can receive input from the console whilst running the server.
# Don't ever do this - it's slow and ugly. (I'm doing it for simplicity's sake)
from _thread import *
import pickle

class Deck:
    def __init__(self):
        self.deck_cards = self.make_cards()
        self.cards_in_play = []

    # to generate all 52 cards
    def make_cards(self):
        cards = []
        for k in 'SHDC':
            for v in range(1, 14):
                cards.append((k, v))
        return cards

    # returns true if there are less than num cards in deck_card
    def is_remaining_cards(self, num):
        if len(self.deck_cards) < num:
            return True
        return False

    # num = number of cards to shuffle from the playing cards except this
    def reshuffle_cards(self, num):
        cards = []
        for card in self.cards_in_play[:-num]:
            if 0 not in card and -5 not in card:
                cards.append(card)

        random.shuffle(cards)
        for card in cards:
            self.deck_cards.append(card)
            self.deck_cards.remove(card)
        random.shuffle(self.deck_cards)

    def get_random_cards(self, n):
        cards = random.sample(self.deck_cards, n)
        for card in cards:
            self.remove_card(card)
        return cards

    def remove_card(self, card):
        self.deck_cards.remove(card)

    def print_cards_in_play(self):
        print("\nLatest cards played on Table =========> [ ", end='')
        for card in self.cards_in_play[-5:]:
            if -5 not in card:
                print(card, end='')
        print(" ] <=======")


class Player:
    def __init__(self, p_id, cards):
        self.p_id = p_id
        self.cards = cards

    def get_cards(self):
        return self.cards

    def cards_with_aces(self, player_cards, k, v_moves, deck):
        for first_c in player_cards:
            if k in first_c:  # spade cards are present
                if 1 in first_c:  # ace of spade is present
                    # for testing
                    if [first_c, 'penalty1'] not in v_moves:
                        v_moves.append([first_c, 'penalty1'])

                    # code for choosing another card - probably function
                    for second_c in player_cards:

                        # when we have 2th card as same as kind of 1st ace
                        if first_c[0] == second_c[0] and (first_c != second_c):
                            v_moves.append([first_c, second_c])

                        # condition will be true if there is 2nd aces
                        if (1 in second_c) and (k not in second_c):

                            # testing
                            if [first_c, second_c, 'penalty1'] not in v_moves:
                                v_moves.append([first_c, second_c, 'penalty1'])

                            for third_c in player_cards:

                                # when we have 3th card as same as kind of 2rd ace
                                if second_c[0] == third_c[0] and second_c != third_c:
                                    v_moves.append([first_c, second_c, third_c])

                                # condition will be true if there is 3rd ace
                                if (1 in third_c) and (k not in third_c) and (second_c[0] not in third_c):

                                    for fourth_c in player_cards:

                                        # testing
                                        if [first_c, second_c, third_c, 'penalty1'] not in v_moves:
                                            v_moves.append([first_c, second_c, third_c, 'penalty1'])

                                        # when we have 4th card as same as kind of 3rd ace
                                        if third_c[0] == fourth_c[0] and third_c != fourth_c:
                                            v_moves.append([first_c, second_c, third_c, fourth_c])

                                        # condition will be true if there is 4th ace
                                        if (1 in fourth_c) and (k not in fourth_c) and (
                                                second_c[0] not in fourth_c) and (third_c[0] not in fourth_c):

                                            # testing
                                            if [first_c, second_c, third_c, fourth_c, 'penalty1'] not in v_moves:
                                                v_moves.append(
                                                    [first_c, second_c, third_c, fourth_c, 'penalty1'])

                                            for fifth_c in player_cards:

                                                # when we have 5th card as same as kind of 4th ace
                                                if fourth_c[0] == fifth_c[0] and fourth_c != fifth_c:
                                                    v_moves.append(
                                                        [first_c, second_c, third_c, fourth_c, fifth_c])

                # if first card is of spades but not ace
                else:
                    if not deck.cards_in_play:
                        v_moves.append([first_c])  # will append if its the first card to be played in game
                    elif deck.cards_in_play[-1][0] == k:
                        v_moves.append([first_c])

        return v_moves

    # Testing purposes
    def valid_cards_all(self, deck):
        cards = []
        for card in deck.cards_in_play[:]:
            if 0 not in card and -5 not in card:
                cards.append(card)
        return cards

    def get_valid_moves(self, deck):
        num = None
        v_moves = []
        player_cards = self.cards

        # if remaining cards are less than 14 and valid_cards_all smaller than 1 then reshuffle leaving last 6 cards
        if len(self.valid_cards_all(deck)) < 1 and deck.is_remaining_cards(14):
            for card in player_cards:
                if card[1] != 5 and card[1] != 11 and card[1] != 1:
                    v_moves = [[card]]
                    deck.reshuffle_cards(6)
                    return v_moves

        if len(deck.cards_in_play) == 0:
            k = 'S'
        else:
            last_card_played = deck.cards_in_play[-1]
            k = last_card_played[0]
            num = abs(last_card_played[1])  # converts -5 to 5 for comparision with last card

            # for special case of 5
            if last_card_played[1] == 5:
                count = 2
                # valid_moves.append(['penalty2'])
                # for checking if player has 5
                for card in player_cards:
                    if card[1] == 5:
                        v_moves.append([card])

                # for checking the how many consecutive 5 were played and deciding no.of penalty cards on that basis
                for card in deck.cards_in_play[-2::-1]:  # loop starts from second last card in played card
                    if card[1] == 5:
                        count += 2
                    else:
                        break
                m = 'penalty' + str(count)
                v_moves.append([m])
                return v_moves

        # when player doesn't want to play any card
        v_moves.append(['penalty1'])

        # for generating all the valid moves
        v_moves = self.cards_with_aces(player_cards, k, v_moves, deck)

        # match number
        for card in player_cards:
            if num == card[1] and card[1] == 1:
                self.cards_with_aces(player_cards, card[0], v_moves, deck)
            elif num == card[1] and card[1] != 1:
                v_moves.append([card])

        # for special case of J (11)
        for first_card in player_cards:
            if first_card[1] == 11 and [first_card] not in v_moves:
                v_moves.append([first_card])
        return v_moves

    # print valid moves
    def print_valid_moves(self, v_moves):
        print('\nCurrent Valid Options are: ')
        for i in range(len(v_moves)):
            # time.sleep(0.3)
            print('{} -> {}'.format(i + 1, v_moves[i]))
        print()

    def has_won(self):
        if len(self.cards) == 0:
            print('=' * 180)
            print("Player {} Won!".format(self.p_id))
            return True
        return False

    def play_move(self, v_moves, deck):
        # for choosing a move from the valid moves
        while True:
            try:
                pos = int(input("Choose which card to play and enter the position of the card: "))
                if pos < 0 or pos > len(v_moves):
                    print("Incorrect input")
                    continue
                else:
                    # time.sleep(0.3)
                    print(v_moves[pos - 1], "is selected to play")
                    break
            except ValueError:
                print('Not a valid number! Try again')
        pos = pos - 1  # indexing starts from 0
        move = v_moves[pos]
        # get the cards that to be played (in c)
        c = []
        for single_card in move:
            if 'penalty' not in single_card:
                c.append(single_card)

        if deck.is_remaining_cards(9):
            deck.reshuffle_cards(4)

        if len(c) > 0:  # i.e, if c has cards
            # add the cards(in c) at the end of played cards list and remove that card from his hand
            for card in c:
                deck.cards_in_play.append(card)
                self.cards.remove(card)

            # special case for J (11)
            if c[-1][1] == 11:
                choice = input('Please specify the kind of cards for the next moves: (S,H,D,C) :').strip().upper()
                while True:
                    if choice not in ('S', 'H', 'D', 'C'):
                        print('Incorrect Input.Choose one from (s, h, d, c) only')
                        choice = input(
                            'Please specify the kind of cards for the next moves: (S,H,D,C) :').strip().upper
                    else:
                        print('You chose: ', choice)
                        break
                deck.cards_in_play.append((choice, 0))

        # for the penalty cards
        for p in move:
            if 'penalty' in p:
                num = int(p[7])  # no of penalty cards

                # check if there are n cards to pick
                try:
                    random_cards = random.sample(deck.deck_cards, num)
                except ValueError:
                    print("It will be considered a draw as no player is playing with spirit of game")
                    exit()

                # add the penalty cards to the hand
                for card in random_cards:
                    self.cards.append(card)
                # remove those penalty cards from deck_list
                for card in random_cards:
                    deck.deck_cards.remove(card)
                # when penalty was more than 1 card
                if num > 1:
                    last_card = deck.cards_in_play[-1]
                    if last_card and (last_card[0], -5) not in deck.deck_cards:
                        deck.cards_in_play.append((last_card[0], -5))

    # returns True if last card
    def is_last_card(self, deck):
        moves = []
        c = []
        if len(self.cards) == 1:
            # print()
            # print('-' * 20, 'LAST CARD', '-' * 20)
            return True
        for card in self.cards:
            if card[0] not in c:
                moves = self.cards_with_aces(self.cards, card[0], moves, deck)
                c.append(card[0])

        for move in moves:
            if len(move) == len(self.cards) and 'penalty1' not in move:
                # print()
                # print('-' * 20, 'LAST CARD', '-' * 20)
                return True

        return False


class Game:
    def __init__(self):
        self.no_of_players = self.input_players()
        self.deck = Deck()
        self.player_list = self.generate_players(self.no_of_players)
        self.game_id = int(str(random.randint(1, 1000000)) + str(random.randint(2322, 100000000000)))


    def input_players(self):
        while True:
            try:
                num = int(input("Enter number of players between 2 and 6: "))
                if not (num < 2 or num > 6):
                    return num
                print("Incorrect_input")
                continue
            except ValueError:
                print('Not a number! Please enter numbers only')

    def generate_players(self, num):
        p = list('ABCDEFGH')
        players = []
        for i in range(0, num):
            cards = self.deck.get_random_cards(5)  # Deal Card to Player
            player = Player(p[i], cards)  # Save Player ID and Card
            players.append(player)
        return players

    def return_hand_cards(self):
        cards = []
        for player in self.player_list:
            cards.append(player.get_cards())
        return cards

    def get_first_player(self):
        current_hand_cards = self.return_hand_cards()
        temp = ('S', 0)
        for hand in current_hand_cards:
            for card in hand:
                if card == ('S', 1):  # for checking ace of spades
                    f = current_hand_cards.index(hand)
                    return self.player_list[f]
                elif 'S' in card:  # for comparing the highest spade card
                    if card[1] > temp[1]:
                        temp = card

        if temp == ('S', 0):  # True if no player got any spade cards
            return random.choice(self.player_list)

        for hand in current_hand_cards:  # Based on higher spade card
            if temp in hand:
                f = current_hand_cards.index(hand)
                return self.player_list[f]

    def get_next_player(self, curr_player):
        if self.player_list.index(curr_player) == len(self.player_list) - 1:
            next_player = self.player_list[0]
        else:
            next_player = self.player_list[self.player_list.index(curr_player) + 1]
        return next_player

    def show_hand_cards(self):
        print("\nCards in each player's hand")
        for i in range(self.no_of_players):
            # time.sleep(0.3)
            print(self.player_list[i].p_id, '==>', self.player_list[i].cards)
        print()

    def run(self):
        curr_player = self.get_first_player()

        while True:
            self.show_hand_cards()

            self.deck.print_cards_in_play()
            print("{}'s turn".format(curr_player.p_id))
            print("{} ==> {}".format(curr_player.p_id, curr_player.get_cards()))

            valid_moves = curr_player.get_valid_moves(self.deck)
            curr_player.print_valid_moves(valid_moves)

            curr_player.play_move(valid_moves, self.deck)
            if curr_player.has_won():
                break

            curr_player = self.get_next_player(curr_player)


class Client(ConnectionListener):
    def __init__(self, host, port):
        self.Connect((host, port))
        self.id = ''
        self.turn = False
        print("Chat client started")
        self.valid_moves = []
        self.deck = None
        self.game = None
        self.num = None

    def choose_mode(self):
        while 1:
            self.play = input('do u want to A)create a custom room or B)want to join friend\'s room: ').strip().lower()
            if self.play == 'a':
                while 1:
                    self.num = int(input('Enter the no of players for this game between 2 and 8: '))
                    if not (self.num < 2 or self.num > 8):
                        print('you chose:', self.num)
                        random_id = str(random.randint(1, 3000)) + str(random.choice('abcdABCD')) + str(random.randint(20, 200000)) + str(random.choice('abcdABCD'))
                        self.room_id = random_id
                        # print('Your custom room_id is {}'.format(self.room_id))
                        connection.Send({'action': 'play_mode', 'play_mode': self.play, 'num': self.num, 'room_id': self.room_id})
                        break
                break
            elif self.play == 'b':
                room_id = input('Enter the room_id created by your friend: ').strip()
                connection.Send({'action': 'play_mode', 'play_mode': self.play, 'room_id': room_id})
                break

    def Loop(self):
        connection.Pump()
        self.Pump()
        if self.turn:
            self.playing()

    def playing(self):
        if self.turn:
            self.print_valid_moves(self.valid_moves)

            self.game.curr_player.play_move(self.valid_moves, self.game.deck)
            if self.game.curr_player.is_last_card(self.game.deck):
                connection.Send({"action": "last_card", "is_last_card": True, 'p_id': self.id})
            if self.game.curr_player.has_won():
                connection.Close()
            connection.Send({"action": "next", "game_obj": (pickle.dumps(self.game).decode('latin-1'))})

            self.turn = self.changeturn()
            print()

    def changeturn(self):
            if self.turn == True:
                return False
            else:
                return True

    def print_turn(self):
        if self.turn == True:
            print("Your turn")
        else:
            print("Not your turn")

    def print_valid_moves(self, v_moves):
        print('\nCurrent Valid Options are: ')
        for i in range(len(v_moves)):
            # time.sleep(0.3)
            print('{} -> {}'.format(i + 1, v_moves[i]))
        print()

    #######################################
    ### Network event/message callbacks ###
    #######################################

    def Network_acknowledge(self, data):
        room_id = data['room_id']
        print('\nYou are added to the room with id {}'.format(room_id))
        total_players = data['room'][room_id]['no_of_players']
        current_players = len(data['room'][room_id]['players'])
        print('Total players {}. Players currently in room {}'.format(total_players, current_players))

    def Network_started(self, data):
        print(data['started'])

    def Network_last_card(self, data):
        if data['is_last_card']:
            print('\n Player {} LAST CARD\n'.format(data['p_id']))

    def Network_validmoves(self, data):
        self.game = pickle.loads(data['game_obj'].encode('latin-1'))
        self.valid_moves = self.game.curr_player.get_valid_moves(self.game.deck)
        self.game.deck.print_cards_in_play()


    def Network_restart(self, data):
        print('Your last game is over')
        print('*'*50)
        self.turn = False

    def Network_mycards(self, data):
        # self.id = data['id']
        print('You are player {}.\nYour cards are: {}'.format(data['id'], data['mycards']))

    def Network_calturn(self, data):
        self.turn = data['turn']
        # print("is my turn: ", self.turn)
        print()

    def Network_assign_id(self, data):
        self.id = data['player_id']

    # built in stuff

    def Network_connected(self, data):
        print("You are connected to the server\n")
        self.choose_mode()

    def Network_error(self, data):
        print('error:', data['error'][0])
        connection.Close()

    def Network_disconnected(self, data):
        print('Server disconnected')
        exit()


if __name__ == '__main__':

    host, port = 'localhost', '21'
    c = Client(host, int(port))
    while 1:
        c.Loop()
        sleep(0.001)
