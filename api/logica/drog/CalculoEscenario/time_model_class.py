__author__ = 'root'


class TimeModelClass:
    def __init__(self, t_hour, date, xyuv, temp=None, wind=None, corr=None):
        self.t_hour = t_hour
        self.date = date
        self.xyuv = xyuv
        self.temp = temp
        self.wind = wind
        self.corr = corr