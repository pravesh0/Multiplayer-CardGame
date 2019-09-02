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


class Game(object):
    def __init__(self, no_of_players):
        self.no_of_players = no_of_players
        self.deck = Deck()
        self.game_id = str(random.randint(1, 10000)) + str(random.choice('abcdABCD')) + str(random.randint(1, 1000000))
        self.room_id = ''

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
        self.player_id = self._server.next_id()
        print('in client __init')



    def Close(self):
        self._server.DelPlayer(self)

    ##################################
    ### Network specific callbacks ###
    ##################################

    def Network_play_mode(self, data):
        print('in networdk_play_mode')
        self._server.play_mode(data, self.player_id)

    def Network_last_card(self, data):
        self._server.display_last_card(data)

    def Network_next(self, data):
        game_obj = pickle.loads(data['game_obj'].encode('latin-1'))
        # print("in next data is id of game obj", id(game_obj))
        self._server.next(game_obj)


class ChatServer(Server):
    channelClass = ClientChannel

    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        print('in server init')
        self.players = []
        self.rooms = []
        self.player_id = -1
        print('Server launched')

    def start(self, no_of_players, room_id):

            self.game = Game(no_of_players)
            self.game.room_id = room_id
            self.game.no_of_players = no_of_players
            self.game.player_list = self.game.generate_players(no_of_players)
            self.game.curr_player = self.game.get_first_player()
            d = "\n\nGame Started \n Shuffling..."
            self.SendToAll({'action': 'started', 'started': d, 'game_obj': pickle.dumps(self.game).decode('latin-1')})
            # self.send_allcards({"action": "allcards", 'cards': self.game.return_hand_cards()})
            self.game.curr_player = self.game.get_first_player()

            self.next_turn()

    def Connected(self, channel, addr):
        print('in connected')
        self.AddPlayer(channel)

    def play_mode(self, data, player_id):
        room_id = data['room_id']
        if data['play_mode'] == 'a':

            # creating the room and then acknowledging the client
            if self.create_room(room_id, data['num'], player_id):
                self.send_acknowledge({'action': 'acknowledge', 'player_id': player_id, 'room_id': room_id, 'room': self.return_room(room_id)})

        elif data['play_mode'] == 'b':
            # adding to the room if that room exists and acknowledging the client
            if self.add_to_rooms(room_id, player_id):
                self.send_acknowledge({'action': 'acknowledge', 'player_id': player_id, 'room_id': room_id, 'room': self.return_room(room_id)})
                if self.is_room_full(room_id):
                    self.start(self.no_of_players_in_room(room_id), room_id)

    def no_of_players_in_room(self, room_id):
        room = None
        for r in self.rooms:
            if room_id in r.keys():
                room = r
                break
        return room[room_id]['no_of_players']

    def players_in_room(self, room_id):
        room = None
        for r in self.rooms:
            if room_id in r.keys():
                room = r
                break
        return room[room_id]['players']

    def is_room_full(self, room_id):
        room = None
        for r in self.rooms:
            if room_id in r.keys():
                room = r
                break
        if room[room_id]['no_of_players'] == len(room[room_id]['players']):
            return True
        return False

    def return_room(self, room_id):
        for room in self.rooms:
            if room_id in room.keys():
                return room

    def add_to_rooms(self, room_id, player_id):
        for room in self.rooms:
            if room_id in room.keys():
                print('Room with room_id {} exists'.format(room_id))
                n = room[room_id]['no_of_players']
                # if room is full
                if n == len(room[room_id]['players']):
                    print('Room is already full')
                    return False
                else:
                    room[room_id]['players'].append(player_id)
                    print('Player {} added to room {}'.format(player_id, room_id))
                    return True
        # if there are no rooms
        else:
            print('No room with room_id {} exists'.format(room_id))
            return False

    def create_room(self, room_id, n, player_id):
        self.rooms.append({room_id: {"no_of_players": n, "players": [player_id,]}})
        print('Room with room_id {} is created'.format(room_id))
        return True

    def send_acknowledge(self, data):
        for player in self.players:
            if data['player_id'] in player.values():
                i = self.players.index(player)
                player_obj = next(iter(self.players[i].keys()))     # return object
                player_obj.Send(data)

    def next(self, game_obj):
        # self.send_mycards(self.game.player_list)
        # print('game object recieved {} and the previous game obj {}'.format(game_obj, self.game))
        self.game = game_obj
        # print('data sent by connection.Send and passed by its channel is', pickle.loads(data).encode('latin-1'))
        # print("in server's next printing self.game.playerlist", self.game.player_list)
        self.game.curr_player = self.game.get_next_player(self.game.curr_player)
        self.next_turn()

    def next_turn(self):
        room_players = self.players_in_room(self.game.room_id)

        for player in self.game.player_list:       # [ a, b, c, d]
            if player == self.game.curr_player:     # for curr_player
                # room_players = self.players_in_room(self.game.room_id)

                p = room_players[self.game.player_list.index(player)]
                # p.Send({'action': 'validmoves', 'game_obj': (pickle.dumps(self.game).decode('latin-1'))})
                # p.Send({'action': 'calturn', 'turn': True})
                # self.players[self.game.player_list.index(player)].Send({'action': 'validmoves', 'game_obj': (pickle.dumps(self.game).decode('latin-1'))})
                # self.players[self.game.player_list.index(player)].Send({'action': 'calturn', 'turn': True})
                # self.send_mycards(self.game.player_list)
                self.send_data(p, {'action': 'validmoves', 'game_obj': (pickle.dumps(self.game).decode('latin-1'))})
                self.send_data(p, {'action': 'calturn', 'turn': True})
                self.send_mycards(self.game)
                break

    def display_last_card(self, data):
        self.SendToAll({'action': 'last_card', 'is_last_card': data['is_last_card'], 'p_id': data['p_id'], 'game_obj': (pickle.dumps(self.game).decode('latin-1'))})

    def send_allcards(self, data):
        print("in send_allcards")
        [p.Send(data) for p in self.players]

    def send_mycards(self, game_obj):
        print("in send_mycards: data is:", game_obj)
        room_players = self.players_in_room(game_obj.room_id)
        for i in range(len(game_obj.player_list)):
            print("sent to data['id']==", i)
            p = room_players[i]
            self.send_data(p, {'action': 'mycards', 'mycards': self.game.player_list[i].cards, 'id' : self.game.player_list[i].p_id})

    def AddPlayer(self, player):
        # print('in add player b')
        self.players.append({player: self.player_id})
        print('players in add player are :', self.players)
        # print("TESTING self.players.append(player) gives:", self.players)
        # self.SendToAll({"action": "players", 'num': [p.player_id for p in self.players]})

    def DelPlayer(self, player):
        print("Deleting Player" + str(player.addr))
        self.remove_player(player)
        self.EndGame({'action': 'restart'})


        # self.start(len(self.players))
        # self.SendPlayers()

    def remove_player(self, player):
        for pl in self.players:
            for p in pl.keys():
                if p == player:
                    self.players.remove(pl)
                    break



    def EndGame(self, data):
        [p.Send(data) for p in self.players]

    def next_id(self):
        self.player_id += 1
        return self.player_id

    # send to specific player having id = player_id
    def send_data(self, player_id, data):
        for player in self.players:
            if player_id in player.values():
                i = self.players.index(player)
                player_obj = next(iter(self.players[i].keys()))     # return object
                player_obj.Send(data)

    def Network(self, data):
        print('in network data is ', data)

    # sends to all the players of a game
    def SendToAll(self, data):
        game_obj = pickle.loads(data['game_obj'].encode('latin-1'))
        room_id = game_obj.room_id
        players_in_room = self.players_in_room(room_id)
        # print('players in room', players_in_room)
        for player in self.players:     # {} {} {} {}
            for p in players_in_room:    #  [0, 1, 2, 3]
                if p == next(iter(player.values())):
                    i = self.players.index(player)
                    player_obj = next(iter(self.players[i].keys()))  # return object
                    player_obj.Send(data)
                    # print('player_obj is ', player_obj, '\nAll players are', self.players)

    def Launch(self):
        while True:
            self.Pump()
            sleep(0.0001)


# get command line argument of server, port
if __name__ == '__main__':

    # host, port = '192.168.56.1', '21'
    host, port = 'localhost', '21'
    s = ChatServer(localaddr=(host, int(port)))
    s.Launch()
