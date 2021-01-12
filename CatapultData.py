class CatapultData:

    def __init__(self, split):

        self.raw_time = int(split[0])
        # self.time = int(split[0])
        self.latLng = (float(split[2]), float(split[3]))        
    
    # def get_XY(self, lat, long):
