import random
import itertools


colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0),
          (255, 0, 255), (255, 255, 0), (0, 255, 255)]

class Buildings:
    MARKET_INCOME = 3
    MARKET_COST = 15
    FORT_COST = 20

    def __init__(self, fort_lvl = 0, market_lvl = 0):
        self.fort_lvl = fort_lvl
        self.market_lvl = market_lvl

    def get_market_income(self):
        return self.MARKET_INCOME * self.market_lvl

    def get_market_cost(self):
        return self.MARKET_COST * self.market_lvl + self.MARKET_COST

    def get_fort_cost(self):
        return self.FORT_COST * self.fort_lvl + self.FORT_COST


class Territory:
    BASE_INCOME = 1
    BASE_CAPTURE_TIME = 3

    def __init__(self, buildings, owner = None):
        self.buildings = buildings
        self.owner = owner

    def get_income(self):
        return self.BASE_INCOME + self.buildings.get_market_income()

    def can_upgr_market(self):
        if self.owner:
            return self.owner.gold >= self.buildings.get_market_cost()
        else:
            return False

    def can_upgr_fort(self):
        if self.owner:
            return self.owner.gold >= self.buildings.get_fort_cost()
        else:
            return False

    def upgr_market(self):
        self.owner.gold = self.owner.gold - self.buildings.get_market_cost()
        self.buildings.market_lvl = self.buildings.market_lvl + 1

    def upgr_fort(self):
        self.owner.gold = self.owner.gold - self.buildings.get_fort_cost()
        self.buildings.fort_lvl = self.buildings.fort_lvl + 1


class Map:
    def __init__(self, players, dim = 10):
        self.dim = dim
        self.players = players
        self.generate_map()

    def generate_map(self):
        self.map = []
        temp_coords = []
        for i in range(self.dim):
            self.map.append([])
            temp_coords.append([])
            for j in range(self.dim):
                self.map[i].append(Territory(Buildings()))
                temp_coords[i].append((i, j))
        temp_coords = list(itertools.chain(*temp_coords))
        random.shuffle(temp_coords)
        random.shuffle(temp_coords)
        for i in range(len(self.players)):
            cur_x = temp_coords[i][0]
            cur_y = temp_coords[i][1]
            self.map[cur_x][cur_y].owner = self.players[i]
            self.players[i].territories.append(self.map[cur_x][cur_y])
            


class Unit:
    def __init__(self, att, defence, ammount, morale):
        self.attack = att
        self.defence = defence
        self.ammount = ammount
        self.morale = morale

    def receive_damage(self, damage):
        units_lost = self.ammount - damage // self.defence
        self.ammount = self.ammount - units_lost
        if self.ammount < 0:
            extra_damage = abs(int(self.ammount))
            self.ammount = 0
            return extra_damage
        else:
            return 0

    def get_health(self):
        return self.ammount * self.defence


class Infantry(Unit):
    def __init__(self, att, defence, ammount, morale):
        super().__init__(att, defence, ammount, morale)


class Cavlary(Unit):
    def __init__(self, att, defence, ammount, morale):
        super().__init__(att, defence, ammount, morale)


class Army:
    def __init__(self, inf, cav, pos_x, pos_y):
        self.troops = (inf, cav)
        self.pos_x = pos_x
        self.pos_y = pos_y

    def fight(self, other):
        damage_done = self.get_damage()
        damage_taken = other.get_damage()
        damage_taken = damage_taken // 2 + self.troops[0].receive_damage(damage_taken // 2)
        self.troops[1].receive_damage(damage_taken)
        damage_done = damage_done // 2 + other.troops[0].receive_damage(damage_done // 2)
        other.troops[1].receive_damage(damage_done)

    def get_damage(self):
        inf_damage = self.troops[0].attack * self.troops[0].ammount
        cav_damage = self.troops[1].attack * self.troops[1].ammount
        return inf_damage + cav_damage

    def get_ammount(self):
        return self.troops[0].ammount + self.troops[1].ammount

    def get_morale(self):
        inf_morale = self.troops[0].morale * self.troops[0].ammount
        cav_morale = self.troops[1].morale * self.troops[1].ammount
        return (inf_morale + cav_morale) / self.get_ammount()

    def move(self, x, y):
        x_change = abs(self.pos_x - x)
        y_change = abs(self.pos_y - y)
        if (x_change + y_change) == 1:
            self.pos_x = x
            self.pos_y = y

    def get_maintenance(self):
        pass


class Player:
    STARTING_GOLD = 30

    def __init__(self, name, color, territories = [], armies = []):
        self.name = name
        self.territories = territories
        self.armies = armies
        self.gold = self.STARTING_GOLD
        self.color = color

    def play_turn(self):
        pass

    def get_income(self):
        for ter in self.territories:
            self.gold = self.gold + ter.get_income()
        for army in self.armies:
            self.gold = self.gold - army.get_maintenance()

    def hire_cav(self, ammount):
        pass


class Game:
    def __init__(self, cnt_players, mode):
        random.shuffle(colors)
        self.players = []
        for i in range(cnt_players):
            self.players.append(Player('Player {}'.format(i), colors[i]))
        self.map = Map(self.players)
        self.map.generate_map()
        self.turn = 1
        #self.start(mode)

    def start(self, mode):
        while(len(self.players) > 1 and self.turn != mode ):
            for player in self.players:
                player.get_income()
                player.play_turn()
            self.turn = self.turn + 1
