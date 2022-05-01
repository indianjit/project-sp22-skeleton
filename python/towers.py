class Tower():
    allTowers = [] # its a list of towers
    def __init__(self, location, instance) -> None:
        self.point = location
        self.cities = []
        self.instance = instance
        self.updateCities()
        Tower.allTowers.append(self)
    def updateCities(self):
        