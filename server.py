import sys, pickle
from time import sleep, localtime
from weakref import WeakKeyDictionary

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel
import random


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


class Game(object):
    def __init__(self):
        self.no_of_players = 0
        self.deck = Deck()


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
        self.player_list = self.generate_players(self.no_of_players)
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


class ClientChannel(Channel):
    """
    This is the server representation of a single connected client.
    """

    def __init__(self, *args, **kwargs):


        Channel.__init__(self, *args, **kwargs)
        self.player_id = str(self._server.next_id())


    def Close(self):
        self._server.DelPlayer(self)

    ##################################
    ### Network specific callbacks ###
    ##################################

    def Network_next(self, data):
        game_obj = pickle.loads(data['game_obj'].encode('latin-1'))
        # print("in next data is id of game obj", id(game_obj))
        self._server.next(game_obj)


    def Network_message(self, data):
        self._server.SendToAll({"action": "message", "message": data['message'], "who": self.nickname})

    def Network_nickname(self, data):
        self._server.SendPlayers()


class ChatServer(Server):
    channelClass = ClientChannel

    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.players = []
        self.player_id = -1
        print('Server launched')


    def start(self, num):
        if num == 2:
            self.game = Game()
            print("printing self.game.deck", self.game.deck)

            self.game.no_of_players = len(self.players)
            self.game.player_list = self.game.generate_players(len(self.players))
            self.game.curr_player = self.game.get_first_player()
            print("TESTING")
            print("self.game.player_list:", self.game.player_list)
            print("self.game.curr_player:", self.game.curr_player)
            print("self.game.return_hand_cards:", self.game.return_hand_cards())
            d = "Game Started \n Shuffling..."
            self.SendToAll(d)
            # self.send_allcards({"action": "allcards", 'cards': self.game.return_hand_cards()})


            self.game.curr_player = self.game.get_first_player()

            self.next_turn()

    def Connected(self, channel, addr):
        self.AddPlayer(channel)

    def numplayer(self, data):
        print('in numplayer')
        [p.Send(data) for p in self.players]
        print('end numplayer')


    def next(self, game_obj):
        # self.send_mycards(self.game.player_list)
        # print('game object recieved {} and the previous game obj {}'.format(game_obj, self.game))
        self.game = game_obj
        # print('data sent by connection.Send and passed by its channel is', pickle.loads(data).encode('latin-1'))
        # print("in server's next printing self.game.playerlist", self.game.player_list)
        self.game.curr_player = self.game.get_next_player(self.game.curr_player)
        self.next_turn()


    def next_turn(self):

        for player in self.game.player_list:
            print('in next_turn"s for, ', self.game.curr_player, player, self.game.player_list)
            if player == self.game.curr_player and len(self.players) >= 2:
                print('in next_turn"s if')
                # print('self.game.deck-------------->', pickle.dumps(self.game.player_list[0].))
                print('mst h klsfjkldjgkdjfd svkjvjkdsvkljs', player.get_cards(), self.game.deck)
                self.players[self.game.player_list.index(player)].Send({'action': 'validmoves', 'player_obj': (pickle.dumps(player).decode('latin-1')), 'deck_obj':(pickle.dumps(self.game.deck).decode('latin-1')), 'game_obj': (pickle.dumps(self.game).decode('latin-1'))})
                self.players[self.game.player_list.index(player)].Send({'action': 'calturn', 'turn': True})
                self.send_mycards(self.game.player_list)

                break




    def send_allcards(self, data):
        print("in send_allcards")
        [p.Send(data) for p in self.players]

    def send_mycards(self, data):
        print("in send_mycards: data is:", data)
        for i in range(len(self.players)):
            print("sent to data['id']==", i)
            print('players', self.players)
            self.players[i].Send({'action': 'mycards', 'mycards': self.game.player_list[i].cards, 'id' : self.game.player_list[i].p_id})

    def AddPlayer(self, player):
        print("New Player" + str(player.addr))
        self.players.append(player)
        # print("TESTING self.players.append(player) gives:", self.players)
        self.SendPlayers()
        print("players", [p for p in self.players])
        self.send_to_specific(len(self.players))
        # self.SendToAll({"action": "players", 'num': [p.player_id for p in self.players]})
        self.start(len(self.players))

    def DelPlayer(self, player):
        print("Deleting Player" + str(player.addr))

        self.EndGame({'action': 'restart'})
        self.players.remove(player)
        self.start(len(self.players))
        # self.SendPlayers()

    def EndGame(self, data):
        [p.Send(data) for p in self.players]

    def next_id(self):
        self.player_id += 1
        return self.player_id

    def SendPlayers(self):
        self.SendToAll({"action": "players", "players": [p.player_id for p in self.players]})

    def send_to_specific(self, data):
        print("in send_to_specific sending data:", data)

        for i in range(data):
            if data == i:
                print("sent to data['id']==", i)
                print('players', self.players)
                self.players[i].Send({'action': 'assign_id', 'data': i})

    def Network(self, data):
        print('in network data is ', data)

    def SendToAll(self, data):
        [p.Send(data) for p in self.players]

    def Launch(self):
        while True:
            self.Pump()
            sleep(0.0001)


# get command line argument of server, port
if __name__ == '__main__':

    host, port = '192.168.56.1', '21'
    s = ChatServer(localaddr=(host, int(port)))
    s.Launch()
