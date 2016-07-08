from logic.twg_player import Player, Offer
from logic.twg_map import Map
from logic.twg_army import Army, Infantry, Cavlary
import random


colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0),
          (255, 0, 255), (255, 255, 0), (0, 255, 255)]
pythons = ["Cleese", "Idle", "Chapman", "Palin", "Jones", "Gilliam"]


class Game:
    def __init__(self, cnt_players):
        random.shuffle(colors)
        random.shuffle(pythons)
        self.players = []
        for i in range(cnt_players):
            self.players.append(Player(pythons[i], colors[i]))
        self.map = Map(self.players)
        self.turn = 1
        self.player = self.players[0]
        self.give_starting_armies()

    def give_starting_armies(self):
        for player in self.players:
            x = player.territories[0].x
            y = player.territories[0].y
            player.armies.append(Army(Infantry(), Cavlary(), x, y, player))

    def start(self, mode):
        while(len(self.players) > 1 and self.turn != mode):
            for self.player in self.players:
                self.player.play_turn()
                self.player.get_income()
                self.player.pay_maintenance()
            for player in self.players:
                if not player.is_eliminated():
                    player.reset_armies()
                else:
                    self.eliminate_players()
            self.turn = self.turn + 1
            for row in self.map.map:
                for ter in row:
                    ter.proceed_siege()

    def eliminate_players(self):
        '''
        Remove eliminated players from the game.
        '''
        eliminated = [x for x in self.players if x.is_eliminated()]
        self.players = [x for x in self.players if not x.is_eliminated()]
        for player in eliminated:
            msg = " was eliminated"
            offer = Offer("message", self.players[0], player, 0, msg)
            self.players[0].offers.append(offer)
