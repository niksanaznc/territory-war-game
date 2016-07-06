import random
import itertools


class Buildings:
    MARKET_INCOME = 3
    MARKET_COST = 15
    FORT_COST = 20

    def __init__(self, fort_lvl=0, market_lvl=0):
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
    BASE_CAP_TIME = 3

    def __init__(self, x, y, buildings, owner=None):
        self.buildings = buildings
        self.owner = owner
        self.x = x
        self.y = y
        self.siege_leader = None
        self.capture_time = 0

    def get_income(self):
        return self.BASE_INCOME + self.buildings.get_market_income()

    def can_upgr_market(self):
        if self.owner and self.owner.is_active() and not self.siege_leader:
            return self.owner.gold >= self.buildings.get_market_cost()
        else:
            return False

    def can_upgr_fort(self):
        if self.owner and self.owner.is_active() and not self.siege_leader:
            return self.owner.gold >= self.buildings.get_fort_cost()
        else:
            return False

    def upgr_market(self):
        self.owner.gold = self.owner.gold - self.buildings.get_market_cost()
        self.buildings.market_lvl = self.buildings.market_lvl + 1

    def upgr_fort(self):
        self.owner.gold = self.owner.gold - self.buildings.get_fort_cost()
        self.buildings.fort_lvl = self.buildings.fort_lvl + 1

    def siege(self, player):
        if not self.siege_leader and self.owner is not player:
            self.siege_leader = player
            self.capture_time = self.BASE_CAP_TIME + self.buildings.fort_lvl

    def proceed_siege(self):
        if self.siege_leader:
            self.capture_time = self.capture_time - 1
            if self.capture_time == 0:
                self.surrender()

    def surrender(self):
        if self.owner:
            self.owner.territories.remove(self)
        self.owner = self.siege_leader
        self.siege_leader = None
        self.owner.territories.append(self)

    def lift_siege(self, player):
        if player is self.siege_leader:
            self.siege_leader = None
            self.capture_time = 0

    def is_sieged(self):
        return self.siege_leader is not None


class Map:
    def __init__(self, players, dim=10):
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
                self.map[i].append(Territory(i, j, Buildings()))
                temp_coords[i].append((i, j))
        temp_coords = list(itertools.chain(*temp_coords))
        random.shuffle(temp_coords)
        random.shuffle(temp_coords)
        for i in range(len(self.players)):
            cur_x = temp_coords[i][0]
            cur_y = temp_coords[i][1]
            self.map[cur_x][cur_y].owner = self.players[i]
            self.players[i].territories.append(self.map[cur_x][cur_y])
#        self.map[1][1].owner = self.players[0] # for tests
#        for i in range(2, len(self.players)):
#        self.players[0].territories.append(self.map[1][1])
#        self.map[1][2].owner = self.players[1]
#        self.players[1].territories.append(self.map[1][2])
