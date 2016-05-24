import random
import itertools

class Buildings:
    MARKET_INCOME = 3

    def __init__(self, fort_lvl = 0, market_lvl = 0):
        self.fort_lvl = fort_lvl
        self.market_lvl = market_lvl

    def get_market_income(self):
        return MARKET_INCOME * market_lvl


class Territory:
    BASE_INCOME = 1
    BASE_CAPTURE_TIME = 3

    def __init__(self, buildings, army):
        self.buildings = buildings
        self.army = army

    def get_income(self):
        return BASE_INCOME + self.buildings.get_market_income()


class Map:
    def __init__(self, dim = 10, players = 2):
        self.dim = dim
        self.players = players
        self.generate_map()

    def generate_map(self):
        self.map = []
        for i in range(self.dim):
            self.map.append([])
            for _ in range(self.dim):
                self.map[i].append(Territory())


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
    def __init__(self, inf, cav):
        self.troops = (inf, cav)

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


class Player:
    pass


class Game:
    pass
