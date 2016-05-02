# -*- coding: utf-8 -*-
"""
Created on Sun May  1 21:21:51 2016

@author: David
"""

from InspectionModel import InspectionModel
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer


def inspectionmodel_draw(restaurant):
    if restaurant is None:
        return
    portrayal = {"Filled": True, "Layer": 0}
    (x, y) = restaurant.get_pos()
    portrayal["x"] = x
    portrayal["y"] = y
    if restaurant.hygiene == 'Good':
        portrayal["Shape"] = 'circle'
        portrayal['r'] = 1
    if restaurant.hygiene == 'Bad':
        portrayal["Shape"] = 'rect'
        portrayal['w'] = 1
        portrayal['h'] = 1
    colors = {'Broadly compliant': 'green',
              'Poorly compliant': 'red',
              'Unrated': 'gray',
              'Closed': 'black'}         
    portrayal["Color"] = colors[restaurant.rating]
    return portrayal

canvas_element = CanvasGrid(inspectionmodel_draw, 20, 20, 500, 500)
restaurant_chart = ChartModule([{"Label": "Good", "Color": "green"},
                          {"Label": "Bad", "Color": "red"}])

server = ModularServer(InspectionModel, [canvas_element, restaurant_chart], "Inspection Model",
                       20, 20, 0.1)
server.launch()
