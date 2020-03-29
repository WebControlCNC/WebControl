from __future__ import print_function
from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
import re
import math
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp




def print_solution(manager, routing, solution):
    """Prints solution on console."""
    print('Objective: {} miles'.format(solution.ObjectiveValue()))
    index = routing.Start(0)
    plan_output = 'Route for vehicle 0:\n'
    route_distance = 0
    while not routing.IsEnd(index):
        plan_output += ' {} ->'.format(manager.IndexToNode(index))
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    plan_output += ' {}\n'.format(manager.IndexToNode(index))
    print(plan_output)
    plan_output += 'Route distance: {}miles\n'.format(route_distance)


# The idea for this class is to minimize the distance of G0 moves (i.e., moves above z-axis of 0.0)
# GCode optimization is not a straight travelling salesperson problem (TSP) because their are distinct start and stop
# coordinates involved.  In a TSP problem, optimizers just minimize the total travel time between discrete locations
# (i.e., cities).  This method would work well if all gcode was drill operations.  However, because each line has a
# start and stop, it doesn't apply.  This is more of a Taxi Cab Problem (TCP) where a taxi driver has a list
# of pickups and dropoffs and wants to optimize his route to minimize the travel time.  Whearas in the TSP, the
# "pickup" and 'dropoff" location is the same, in the TCP, they are different.
#
# The problems associated with optimizing gcode are:
#   1. Use of relative positioning will be challenging.  Solution might be to disallow in optimization
#   2.

# https://github.com/ezstoltz/genetic-algorithm/blob/master/genetic_algorithm_TSP.ipynb

class Path:
    x0 = 0 # beginning x,y of the gcode group
    y0 = 0
    x1 = 0 # end x,y of the gcode group
    y1 = 0
    startLine = 0 # index of first gcode line of gcode group in gcode file
    finishLine = 0 # index of last gcode line of gcode group in gcode file
    tool = 0

    def __init__(self, x0, y0, x1, y1, startLine, finishLine, tool):
        if x0 is not None:
            self.x0 = float(x0)
        else:
            self.x0 = None
        if y0 is not None:
            self.y0 = float(y0)
        else:
            self.y0 = None
        if x1 is not None:
            self.x1 = float(x1)
        else:
            self.x1 = None
        if y1 is not None:
            self.y1 = float(y1)
        else:
            self.y1 = None
        self.startLine = startLine
        self.finishLine = finishLine
        self.tool = tool
        print(self)

    def __repr__(self):
        return "[("+str(self.x0)+","+str(self.y0)+")-("+str(self.x1)+","+str(self.y1)+") ("+str(self.startLine)+":"+str(self.finishLine)+") ("+str(self.tool)+")]"


def getXYFromGCode(gCodeLine, xTarget, yTarget):
    gCodeLine = gCodeLine.upper() + " "
    x = re.search("X(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
    if x:
        xTarget = float(x.groups()[0])
    y = re.search("Y(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
    if y:
        yTarget = float(y.groups()[0])

    return xTarget, yTarget

def getZFromGCode(gCodeLine):
    gCodeLine = gCodeLine.upper() + " "
    zTarget = None
    z = re.search("Z(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
    if z:
        zTarget = float(z.groups()[0])
    return zTarget

def isComment(line):
    comment1 = line.find("(")
    comment2 = line.find(";")
    if comment1 == 0 or comment2 == 0:
        return True
    return False

def stripComments(line):
    comment1 = line.find("(")
    if comment1 != -1:
        line = line[:comment1]
    comment1 = line.find(";")
    if comment1 != -1:
        line = line[:comment1]
    line = (line + " ")
    return line

def findInLine(line, code, len):
    gPos = line.find(code)
    gString = line[line.find(code): line.find(code) + len]
    return gString

def getNumberAfterCode(line, code):
    cPos = line.find(code)
    number = line[cPos+1:]  # slice off the T
    return number

class GCodeOptimizer(MakesmithInitFuncs):

    def __init__(self):
        # can't do much because data hasn't been initialized yet
        pass

    def optimize(self):
        # find max z:
        maxZTarget = 0
        units = None
        for line in self.data.gcode:
            line = stripComments(line)
            gString = line[line.find("G"): line.find("G") + 3]
            if gString == "G21":
                if units is not None and units != "G21":
                    print("Error, units switch in file")
                    return False
                units = "G21"
            if gString == "G20":
                if units is not None and units != "G20":
                    print("Error, units switch in file")
                    return False
                units = "G20"
            if gString == "G00" or gString == "G0 ": #found G0/G00
                zTarget = getZFromGCode(line)
                if zTarget is not None:
                    if float(zTarget) > float(maxZTarget):
                        maxZTarget = zTarget
        pathList = []
        inPath = False
        index = 0
        startLine = 0
        startX = None
        startY = None
        currentX = None
        currentY = None
        inHeader = True
        headerEnd = 0
        tool = 0
        toolList = [0]
        footerStart = 0
        #path list will hold the parsed gcode groups between G0 moves.
        for line in self.data.gcode:
            line = stripComments(line)
            tString = findInLine(line, "T", 2) # search for tool command
            if len(tString) > 1:
                toolVal = getNumberAfterCode(line, "T")
                toolVal = int(toolVal)
                print(line)
                print(toolVal)
                if toolVal != tool:
                    if inPath: #close off current path
                        endX = currentX
                        endY = currentY
                        pathList.append(
                            Path(x0=startX, y0=startY, x1=endX, y1=endY, startLine=startLine, finishLine=index, tool=tool))
                        #currentX, currentY = getXYFromGCode(line, currentX, currentY) #there won't be a currentX, currentY in this code
                        inPath = False
                    toolList.append(toolVal)
                    tool = toolVal
                    print("Current tool is now: "+str(tool))
            gString = findInLine(line, "G", 3)
            if True:
                if gString == "G00" or gString == "G0 ": #found G0/G00
                    if not inPath:
                        if currentX is None and currentY is None:
                            startX, startY = getXYFromGCode(line, currentX, currentY)
                            currentX = startX
                            currentY = startY
                            inHeader = False
                        else:
                            startX = currentX
                            startY = currentY
                            endX, endY = getXYFromGCode(line, currentX, currentY)
                            currentX = endX
                            currentY = endY
                            inHeader = False
                    else:
                        endX = currentX
                        endY = currentY
                        pathList.append(Path(x0=startX, y0=startY, x1=endX,y1=endY, startLine=startLine, finishLine=index, tool=tool))
                        currentX, currentY = getXYFromGCode(line, currentX, currentY)
                        inPath = False

                elif gString == "G01" or gString == "G1 " or gString == "G02" or gString == "G2 " or gString == "G03" or gString == "G3 ": #found G1/G01/G2/G02/G3/G03
                    endX, endY = getXYFromGCode(line, currentX, currentY)
                    if startX is None or startY is None:
                        headerEnd = index
                    else:
                        if not inPath:
                            startLine = index
                            startX = currentX
                            startY = currentY
                        if endX is None:
                            endX = startX
                        if endY is None:
                            endY = startY
                        currentX = endX
                        currentY = endY
                        inPath = True
                        inHeader = False
                else:
                    if inHeader:
                        headerEnd = index
            #print(line)
            #print(str(inPath)+"=>"+ str(startX) + ", " + str(startY)+" - "+str(currentX) + ", " + str(currentY))
            index = index + 1

        #print("last"+str(inPath)+"=>"+ str(startX) + ", " + str(startY)+" - "+str(currentX) + ", " + str(currentY))

        newGCode = []
        newGCode.append(units)
        for i in range(0, headerEnd+1):
            line = self.data.gcode[i]
            gString = line[line.find("G"): line.find("G") + 3]
            if gString != "G21" and gString != "G20": # don't setup units anymore
                newGCode.append(self.data.gcode[i])

        #repeat for each tool:
        print("ToolList")
        print(toolList)
        for tool in toolList:
            """Entry point of the program."""
            # Instantiate the data problem.
            newGCode.append("M6 T"+str(tool))
            data = create_data_model(pathList, tool)
            if len(data['locations']) > 0: #could be nulled out because first tool is not 0
                manager = pywrapcp.RoutingIndexManager(len(data['locations']), data['num_vehicles'], data['depot'])
                routing = pywrapcp.RoutingModel(manager)
                distance_matrix = compute_euclidean_distance_matrix(data['locations'])

                def distance_callback(from_index, to_index):
                    """Returns the distance between the two nodes."""
                    # Convert from routing variable Index to distance matrix NodeIndex.
                    from_node = manager.IndexToNode(from_index)
                    to_node = manager.IndexToNode(to_index)
                    return distance_matrix[from_node][to_node]

                transit_callback_index = routing.RegisterTransitCallback(distance_callback)
                routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
                search_parameters = pywrapcp.DefaultRoutingSearchParameters()
                search_parameters.first_solution_strategy = (
                    routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
                solution = routing.SolveWithParameters(search_parameters)
                if solution:
                    print_solution(manager, routing, solution)

                """Prints solution on console."""
                index = routing.Start(0)
                route_distance = 0
                while not routing.IsEnd(index):
                    pathIndex = manager.IndexToNode(index)
                    startLine = data['locations'][pathIndex][4]
                    finishLine = data['locations'][pathIndex][5]
                    newGCode.append("G0 Z" + str(maxZTarget))
                    newGCode.append("G0 X" + str(data['locations'][pathIndex][0]) + " Y" + str(data['locations'][pathIndex][1]))
                    line = self.data.gcode[startLine]
                    gString = line[line.find("G"): line.find("G") + 3]
                    if gString == "G01" or gString == "G1 ":  # found G0/G00
                        X, Y = getXYFromGCode(line, None, None)
                        if X is None and Y is None:
                            zTarget = getZFromGCode(line)
                            if float(zTarget) < 0:
                                newGCode.append("G0 Z0.5")
                    for i in range(startLine, finishLine):
                        newGCode.append(self.data.gcode[i])
                    previous_index = index
                    index = solution.Value(routing.NextVar(index))
                    route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
            else:
                print("No locations for tool"+str(tool))

        newGCode.append("G0 Z" + str(maxZTarget))
        newGCode.append("G0 X" + str(currentX) + " Y" + str(currentY))

        print('Objective: {} units\n'.format(solution.ObjectiveValue()/100))
        print('Path distance: {} units\n'.format(route_distance/100))

        '''
        for path in bestRoute:
            newGCode.append("G0 Z" + str(maxZTarget))
            newGCode.append("G0 X" + str(path.x0) + " Y" + str(path.y0))
            #print("G0 Z" + str(maxZTarget))
            #print("G0 X" + str(path.x0) + " Y" + str(path.y0))
            for i in range(path.startLine, path.finishLine ):
                newGCode.append(self.data.gcode[i])
                #print(self.data.gcode[i])
        '''
        finalGCode = ""
        for i in newGCode:
            finalGCode = finalGCode + i + "\n"
        self.data.actions.updateGCode(finalGCode)

        return True






def create_data_model(pathList, tool):
    """Stores the data for the problem."""
    data = {}
    data['locations'] = []
    # Locations in block units
    for path in pathList:
        if path.tool == tool:
            data['locations'].append( (path.x0, path.y0, path.x1, path.y1, path.startLine, path.finishLine ) )
    data['num_vehicles'] = 1
    data['depot'] = 0
    return data

def compute_euclidean_distance_matrix(locations):
    """Creates callback to return distance between points."""
    distances = {}
    for from_counter, from_node in enumerate(locations):
        distances[from_counter] = {}
        for to_counter, to_node in enumerate(locations):
            if from_counter == to_counter:
                distances[from_counter][to_counter] = 0
            else:
                # Euclidean distance
                distances[from_counter][to_counter] = (int(100*
                    math.hypot((from_node[2] - to_node[0]),
                               (from_node[3] - to_node[1]))))
    return distances