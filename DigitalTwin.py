from pyrex import BioReactSys, WaveReactor, TwinData


class DigitalTwin:
    def __init__(self):
        self.data = TwinData()
        self.reactor = WaveReactor()
        self.reactor.con_dc(self.data)
        self.reaction = BioReactSys()
        self.reaction.con_dc(self.data)
        self.data.agit = 60
        self.data.biomass = 0
        self.data.glucose = 6.83
        self.data.lac = 0

    def update(self):
        self.reactor.update()
        self.reaction.update()
