import city as c

class Connection():
    concentration = 1

    def __init__(self, origin, destination):
        self.origin = origin
        self.destination = destination
        self.size = self._euclidean(self.origin, self.destination)

    def __repr__(self):
        s = str(self.origin.cId) + '|' +  str(self.destination.cId) 
        return s

    # x and y are vectors of the same size
    def _euclidean(self, c1, c2):
        x = [c1.x, c1.y]
        y = [c2.x, c2.y]
        sumSq = 0.0
        for i in range(len(y)):
            sumSq += (x[i] - y[i]) ** 2
        return (sumSq ** 0.5)
