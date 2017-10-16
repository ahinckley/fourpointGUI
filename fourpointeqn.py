from __future__ import division
from sympy import *
import numpy as np
import math

class FourPointCalculation():
    def __init__(self,provider = None):
        if provider:
            self.data = provider
            dimensions = self.data.GetDimensions()
            R_values = self.data.R
        else:
            raw_dimensions = [0.1, 0.25*25.4, 0.001*25.4, 0] #raw_input("Enter dimensions [s,d,t,a] in cm: ")
            variables = ['s','d','t','a']
            dimensions = zip(variables,raw_dimensions)
            R_values = [100, 100, 101]#raw_input("Enter resistance array (Ohm): ")

        self.shape = 'circle'
        if dimensions[3][1]:
            self.shape = 'rectangle'
        afactor_sym, tfactor_sym = self.geometryfactors()
        self.geom_factor_sym = afactor_sym*tfactor_sym

        area_factor = float(afactor_sym.subs(dimensions))
        thickness_factor = float(tfactor_sym.subs(dimensions))
        # get data
        resistance = np.mean(R_values)
        self.sheetresistivity = resistance * area_factor  # Ohm/sq
        self.resistivity = self.sheetresistivity * thickness_factor  # Ohm*cm
        self.conductivity = 1 / self.resistivity  # S/cm
        self.uncertainty = self.getuncertainty(dimensions,R_values) #S/cm
        print("Conductivity = "+str(self.conductivity)+" +/- "+str(self.uncertainty)+" S/cm")

    def getuncertainty(self,dimensions,R):
        # Uses the variance formula for engineers & scientists:
        # standard_dev[F(x,y,..)] = [((df/dx)*s_x)^2 + ((df/dy)*s_y)^2 + ....]^(1/2)
        # where df/dx = partial derivative of F in x, s_x = standard_dev(x) ~ measurement precision
        uncertainty_dim = []
        if self.shape == 'circle':
            dimensions = dimensions[:-1]
        for variable, dim in dimensions:
            precision = self.getprecision(dim)
            variance = (5 * 10**(-precision - 1))**2
            partial_deriv_sym = Derivative(self.geom_factor_sym,variable).doit()
            partial_deriv = partial_deriv_sym.subs(dimensions)
            uncertainty_dim.append(partial_deriv**2*variance)

        resistance_variance = np.std(R) ** 2
        resistance = np.mean(R)
        resistance_partialderiv = -self.geom_factor_sym.subs(dimensions)/resistance**2
        uncertainty_R = resistance_partialderiv**2*resistance_variance
        return float(sqrt(sum(uncertainty_dim)+uncertainty_R))

    def getprecision(self, value):
        return len(str(value).split('.')[1])

    def geometryfactors(self):
        s,d,t,a,m = symbols("s d t a m")
        # calculate area factor based on sample shape
        if self.shape == 'rectangle':
            Am = 1/m * exp(-2*pi*m/d*(a-2*s)) * (1 - exp(-6*pi*m*s/d)) * (1 - exp(-2*pi*m*s/d)) / (1 + exp(-2*pi*a*m/d))
            Ams = Am.series(m,1,100)
            # TODO write sum over m to specific precision
            C1 = pi * s / d + log(1 - exp(-4 * pi * s / d)) - log(1 - exp(-2 * pi * s / d)) + Ams
            area_factor = pi/C1
        else:
            C1 = log(2) + log((d/s) ** 2 + 3) - log((d/s) ** 2 - 3)
            area_factor = pi / C1
        # calculate thickness factor (same for both shapes)
        thickness_factor = 2*pi* s * (t/s) / (2*log(sinh(t/s) / sinh(t/s/2)))
        return area_factor, thickness_factor

if __name__ == "__main__":
    conductivity = FourPointCalculation()
    print(conductivity)
