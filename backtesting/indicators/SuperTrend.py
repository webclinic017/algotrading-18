import backtrader as bt


class SuperTrend(bt.Indicator):
    """
    Super Trend indicator
    """
    lines = ('super_trend', 'upper_to_lower_crossover', 'lower_to_upper_crossover')
    plot_info = dict(subplot=False)

    def __init__(self, period, multiplier):
        self.period = period
        self.stb = SuperTrendBand(period=period, multiplier=multiplier)

    def next(self):
        if len(self) - 1 == self.period:
            self.l.super_trend[0] = self.stb.final_ub[0]
            self.l.upper_to_lower_crossover[0] = 0
            self.l.lower_to_upper_crossover[0] = 0
            return

        if self.l.super_trend[-1] == self.stb.final_ub[-1]:
            if self.data.close[0] <= self.stb.final_ub[0]:
                self.l.super_trend[0] = self.stb.final_ub[0]
                self.l.upper_to_lower_crossover[0] = 0
            else:
                self.l.super_trend[0] = self.stb.final_lb[0]
                self.l.upper_to_lower_crossover[0] = 1

        if self.l.super_trend[-1] == self.stb.final_lb[-1]:
            if self.data.close[0] >= self.stb.final_lb[0]:
                self.l.super_trend[0] = self.stb.final_lb[0]
                self.l.lower_to_upper_crossover[0] = 0
            else:
                self.l.super_trend[0] = self.stb.final_ub[0]
                self.l.lower_to_upper_crossover[0] = 1


class SuperTrendBand(bt.Indicator):
    lines = ('basic_ub', 'basic_lb', 'final_ub', 'final_lb')

    def __init__(self, period, multiplier):
        self.period = period
        self.atr = bt.indicators.AverageTrueRange(period=period)
        self.l.basic_ub = ((self.data.high + self.data.low) / 2) + (self.atr * multiplier)
        self.l.basic_lb = ((self.data.high + self.data.low) / 2) - (self.atr * multiplier)

    def next(self):
        if len(self) - 1 == self.period:
            self.l.final_ub[0] = self.l.basic_ub[0]
            self.l.final_lb[0] = self.l.basic_lb[0]
        else:
            # =IF(OR(basic_ub<final_ub*,close*>final_ub*),basic_ub,final_ub*)
            if self.l.basic_ub[0] < self.l.final_ub[-1] or self.data.close[-1] > self.l.final_ub[-1]:
                self.l.final_ub[0] = self.l.basic_ub[0]
            else:
                self.l.final_ub[0] = self.l.final_ub[-1]

            # =IF(OR(baisc_lb > final_lb *, close * < final_lb *), basic_lb *, final_lb *)
            if self.l.basic_lb[0] > self.l.final_lb[-1] or self.data.close[-1] < self.l.final_lb[-1]:
                self.l.final_lb[0] = self.l.basic_lb[0]
            else:
                self.l.final_lb[0] = self.l.final_lb[-1]
