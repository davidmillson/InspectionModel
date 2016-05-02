# -*- coding: utf-8 -*-
"""
Created on Sun May  1 21:20:57 2016

@author: David
"""

import random

from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import Grid
from mesa.datacollection import DataCollector


class RestaurantCell(Agent):
    '''
    A restaurant cell.

    Attributes:
        x, y: Grid coordinates
        hygiene: Can be "Good" or "Bad"
        rating: Can be "Broadly compliant", "Poorly compliant", "Unrated" or 
        "Closed"
        savings: Numerical
        unique_id: (x,y) tuple.

    unique_id isn't strictly necessary here, but it's good
    practice to give one to each agent anyway.
    '''
    def __init__(self, pos):
        '''
        Create a new restaurant.
        Args:
            pos: The restaurant's coordinates on the grid.
        '''
        self.pos = pos
        self.unique_id = pos
        self.hygiene = 'Good'
        self.rating = 'Closed'
        self.weeks_to_inspection = 0        
        self.savings = 0

    def step(self, model):
        '''
        If the restaurant is due for inspection, test to rate it.
        '''
        if self.rating != 'Closed':
            if self.weeks_to_inspection == 0:
                if random.random() < 0.75:
                    self.inspect()
            else:
                self.weeks_to_inspection -= 1
        '''
        If the restaurant is closed, test to open it.
        '''
        if self.rating == 'Closed':
            self.start_up()
        '''
        If the restaurant is open, calculate revenue, update savings, and 
        check whether or not the restaurant stays open.
        '''
        if self.rating != 'Closed':
            revenue = self.get_revenue()
            self.savings += revenue
            if revenue < 0:
                if random.random() > revenue/10:
                    self.close()
            
    def start_up(self):
        
        hygiene_prob = 0.5        
        
        if random.random() < hygiene_prob:
            self.hygiene = 'Good'
        else:
            self.hygiene = 'Bad'
        self.rating = 'Unrated'        
        self.savings = 10
        
    def close(self):
        self.hygiene = 'Good'
        self.rating = 'Closed'
        self.savings = 0
        self.weeks_to_inspection = 0
    
    def inspect(self):
        
        test_good = 0.8
        test_bad = 0.8        
        
        if self.hygiene == 'Good':
            if random.random() < test_good:
                self.rating = 'Broadly compliant'
                self.weeks_to_inspection = 75 - int(5*random.random())
            else:
                self.rating = 'Poorly compliant'
                self.weeks_to_inspection = 25 - int(5*random.random())
        else:
            if random.random() < test_bad:
                self.rating = 'Poorly compliant'
                self.weeks_to_inspection = 25 - int(5*random.random())
            else:
                self.rating = 'Broadly compliant'
                self.weeks_to_inspection = 75 - int(5*random.random())
    
    def get_revenue(self):
        
        bonus_bc = 0.05
        handicap_nbc = -0.05
        handicap_good = -0.0125
        
        if self.rating == 'Broadly compliant':
            rating_adjustment = bonus_bc
        elif self.rating == 'Poorly compliant':
            rating_adjustment = handicap_nbc
        else:
            rating_adjustment = 0
            
        if self.hygiene == 'Good':
            hygiene_adjustment = handicap_good
        else:
            hygiene_adjustment = 0
        
        revenue = 10 * (random.random() + rating_adjustment + hygiene_adjustment - 0.07)
        
        return revenue

    def get_pos(self):
        return self.pos


class InspectionModel(Model):
    '''
    Simple Restaurant Inspection model.
    '''
    def __init__(self, height, width, density):
        '''
        Create a new restaurant inspection model.

        Args:
            height, width: The size of the grid to model
            density: What fraction of grid cells have a restaurant in them.
        '''
        # Initialize model parameters
        self.height = height
        self.width = width
        self.density = density

        # Set up model objects
        self.schedule = RandomActivation(self)
        self.grid = Grid(height, width, torus=False)

        self.datacollector = DataCollector(
            {"Good": lambda m: self.count_type(m, "Good"),
             "Bad": lambda m: self.count_type(m, "Bad")})

        # Place a restaurant in each cell with Prob = density
        for (contents, x, y) in self.grid.coord_iter():
            if random.random() < self.density:
                # Create a restaurant
                new_restaurant = RestaurantCell((x, y))
                self.grid._place_agent((x, y), new_restaurant)
                self.schedule.add(new_restaurant)
        self.running = True

    def step(self):
        '''
        Advance the model by one step.
        '''
        self.schedule.step()
        self.datacollector.collect(self)

    @staticmethod
    def count_type(model, restaurant_hygiene):
        '''
        Helper method to count restaurants in a given condition in a given model.
        '''
        count = 0
        for restaurant in model.schedule.agents:
            if restaurant.hygiene == restaurant_hygiene and restaurant.rating != 'Closed':
                count += 1
        return count
