class Territory:
    pass


class Unit:
    def __init__(self, att, defence, ammount, morale):
        self.attack = att
        self.defence = defence
        self.ammount = ammount
        self.morale = morale


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
