# -*- coding: utf-8 -*-


######################################################################
#                                                                    #
# This file is part of IfcChecker                                    #
#                                                                    #
# CheckerRules module contains 5 types of checks:checking elements,  #
# properties, attributes, elements on the floor, spaces in rooms     #
#                                                                    #
######################################################################


import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.selector
import OCC
from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Lin
import operator
ops = { ">": operator.gt, "<": operator.lt, "=": operator.eq,
       "!=": operator.ne, ">=":operator.ge, "<=": operator.le }



def CheckingElements (row, m, checking_elements, CSVtable):
    '''
    Сheck if there is at least one specified element in the model
    
    Parameters
    ----------
    row : dict
        a line in the CSV file with the specified IfcElement type.
    m : class 'ifcopenshell.file.file'
        Ifc File.
    checking_elements : list
        the list for BCF to which the list with the error information will be added.
    CSVtable : list
        the list for CSV to which the list with the error information will be added.

    Returns
    -------
    checking_elements : list
        + [Type of element, GlobalID, Titel of issue, Comment for issue, IfcElement]
        e.g. [„IfcWall“, “1AWB_PzwPExQGFZX0DHwpa”, „Checking the properties IsExternal”,
              ”The property is not specified”,#138467 = IFCWALLSTANDARDCASE
              ('1AWB_PzwPExQGFZX0DHwpa', #1, 'Involucro 2497',...)].
    CSVtable : list
        Similar to a list, but without an IfcElement.
    '''
    
    if row["Property_name"] == "" or None:
        if row["Attribute"] == "" or None:
            elements = m.by_type(row["Element"])
            if len(elements) == 0:
                comment = "Elements don't exist"
                titel = "Сhecking for {}".format(row["Element"])
                checking_elements.append ([row["Element"], "", titel, comment, ""])
                CSVtable.append ([row["Element"], "", titel, comment])
    return checking_elements, CSVtable



def CheckingProperty (row, m, checking_elements, CSVtable):
    '''
    Checking whether all elements have the specified property or
    comparing its value with the desired one
    
    Parameters
    ----------
    row : dict
        a line in the CSV file with the specified IfcElement type.
    m : class 'ifcopenshell.file.file'
        Ifc File.
    checking_elements : list
        the list for BCF to which the list with the error information will be added.
    CSVtable : list
        the list for CSV to which the list with the error information will be added.

    Returns
    -------
    checking_elements : list
        + [Type of element, GlobalID, Titel of issue, Comment for issue, IfcElement]
        e.g. [„IfcWall“, “1AWB_PzwPExQGFZX0DHwpa”, „Checking the properties IsExternal”,
              ”The property is not specified”,#138467 = IFCWALLSTANDARDCASE
              ('1AWB_PzwPExQGFZX0DHwpa', #1, 'Involucro 2497',...)].
    CSVtable : list
        Similar to a list, but without an IfcElement.
    '''
    
    if row["Property_name"] != "":
        for element in m.by_type(row["Element"]):
            comment = None
            titel = None
            existence_property = []
            for definition in element.IsDefinedBy:
                if definition.is_a("IfcRelDefinesByProperties"):
                    property_set = definition.RelatingPropertyDefinition
                    if hasattr(property_set,"HasProperties"):
                        for property_name in property_set.HasProperties:
                            if property_name.Name == row["Property_name"]:
                                existence_property.append (1)
                                if str (property_name.NominalValue.wrappedValue) == None or "":
                                    comment = "The Value of Property failed"
                                if row["Value"] != "" or None:
                                    if str (property_name.NominalValue.wrappedValue) != row["Value"]:
                                        comment = "Incorrect Value of Property"
            if existence_property == []:
                comment = "The property is not specified"
            if comment != None:
                titel = "Сhecking the properties {}".format(row["Property_name"])
                checking_elements.append ([row["Element"], element.GlobalId, titel, comment, element])
                CSVtable.append ([row["Element"], element.GlobalId, titel, comment])
    return checking_elements, CSVtable



def CheckingAttribute (row, m, checking_elements, CSVtable):
    '''
    Checking whether the specified attribute has a value for all elements or
    comparing it with the desired specified value
    
    Parameters
    ----------
    row : dict
        a line in the CSV file with the specified IfcElement type.
    m : class 'ifcopenshell.file.file'
        Ifc File.
    checking_elements : list
        the list for BCF to which the list with the error information will be added.
    CSVtable : list
        the list for CSV to which the list with the error information will be added.

    Returns
    -------
    checking_elements : list
        + [Type of element, GlobalID, Titel of issue, Comment for issue, IfcElement]
        e.g. [„IfcWall“, “1AWB_PzwPExQGFZX0DHwpa”, „Checking the properties IsExternal”,
              ”The property is not specified”,#138467 = IFCWALLSTANDARDCASE
              ('1AWB_PzwPExQGFZX0DHwpa', #1, 'Involucro 2497',...)].
    CSVtable : list
        Similar to a list, but without an IfcElement.
    '''
    
    if row["Attribute"] != "":
        for element in m.by_type(row["Element"]):
            comment = None
            titel = None
            existence_attribute = []
            s = row["Attribute"]
            tokens = s.split(".")
            e = element
            for token in tokens:
                a = getattr(e,token)
                e = a
            if a != None:
                existence_attribute.append (1)
                if not isinstance(e, str):
                    if float(e) == None:
                        comment = "The Value of Attribute failed"
                    if row["Value"] != "" or None:    
                        if ops [row["Relation"]](float(e),float(row["Value"])):
                            pass
                        else:
                            comment = "Incorrect Value of Attribute"
                else:
                    if e == None:
                        comment = "The Value of Attribute failed"
            if existence_attribute == []:
                comment = "The attribute is not specified"
            if comment != None:
                titel = "Сhecking the attributes {} in {}".format(row["Attribute"],(row["Element"]))
                if hasattr(element,"GlobalId"):
                    GlId = element.GlobalId
                else:
                    GlId = ""
                checking_elements.append ([row["Element"], GlId, titel, comment, element])
                CSVtable.append ([row["Element"], GlId, titel, comment])
    return checking_elements, CSVtable



def Floor (m, Box, storeys_dic, Level_name,  checking_elements, CSVtable):
    '''
    Verification of the correspondence between the real and the indicated floor
    of the element

    Parameters
    ----------
    m : class 'ifcopenshell.file.file'
        Ifc File.
    Box : Bnd_Box
        box around the model from module ImportIFC.Model.ModelBox.
    storeys_dic : dict
        Structured information about floors from module ImportIFC.Model.Floors.
    Level_name : str
        name specified by the user.
    checking_elements : list
        the list for BCF to which the list with the error information will be added.
    CSVtable : list
        the list for CSV to which the list with the error information will be added.

    Returns
    -------
    checking_elements : list
        + [Type of element, GlobalID, Titel of issue, Comment for issue, IfcElement]
        e.g. [„IfcWall“, “1AWB_PzwPExQGFZX0DHwpa”, „Checking the properties IsExternal”,
              ”The property is not specified”,#138467 = IFCWALLSTANDARDCASE
              ('1AWB_PzwPExQGFZX0DHwpa', #1, 'Involucro 2497',...)].
    CSVtable : list
        Similar to a list, but without an IfcElement.
    '''
   
    #checking floors
    tree_settings = ifcopenshell.geom.settings()
    tree_settings.set(tree_settings.DISABLE_OPENING_SUBTRACTIONS, True)
    t = ifcopenshell.geom.tree(m, tree_settings)

    WrongElements = []
    level_name = Level_name

    ind_level = storeys_dic[level_name]["Index"]
    name = next((k for k in storeys_dic if storeys_dic[k]["Index"] == ind_level+1), None)
    if name!= None:
        slabs = ifcopenshell.util.selector.Selector().parse(m,'@ #{} & .IfcSlab'.format(storeys_dic[name]["GlobalId"]))
        shape_slabs = [i.Items for s in slabs\
                       for i in s.Representation.Representations\
                    if i.RepresentationType == 'SweptSolid' and i.RepresentationIdentifier == 'Body']
        depth_slabs = [i.Depth for s in shape_slabs for i in s if i.is_a("IfcExtrudedAreaSolid")]
        if depth_slabs != []:
            H = max(depth_slabs) + 0.01
        else:
            H = 0.01
    else:
        H = 0.01
    
    CornerMax = Box.CornerMax() #Maximum coordinates
    CornerMin = Box.CornerMin() #Minimum coordinates

    GeometryFloor = t.select_box(((CornerMin.X(),CornerMin.Y(),storeys_dic[level_name]["minZ"]+0.01),\
                                  (CornerMax.X(),CornerMax.Y(),storeys_dic[level_name]["maxZ"]-H)),\
                                 completely_within = True)
    
    for element in GeometryFloor:
        if not element.is_a("IfcSpace"):
            if element.Representation:
                for Structure in element.ContainedInStructure:
                    if Structure.RelatingStructure.is_a("IfcBuildingStorey"):
                        if storeys_dic[level_name]["GlobalId"] != Structure.RelatingStructure.GlobalId:
                            WrongElements.append (element)
                            
            if element.is_a('IfcFurnishingElement'):
                if Structure.is_a('IfcRelContainedInSpatialStructure'):
                    for agg in Structure.RelatingStructure.Decomposes:
                        if agg.is_a('IfcRelAggregates'):
                            if storeys_dic[level_name]["GlobalId"] != agg.RelatingObject.GlobalId:
                                WrongElements.append (element)
                                

    IndicatedSlabs = ifcopenshell.util.selector.Selector().parse(m,'@ #{} & .IfcSlab'.format(storeys_dic[level_name]["GlobalId"]))

     
    shape = [i.Items for s in IndicatedSlabs\
             for i in s.Representation.Representations\
            if i.RepresentationType == 'SweptSolid' and i.RepresentationIdentifier == 'Body']
    depth = [i.Depth for s in shape for i in s if i.is_a("IfcExtrudedAreaSolid")]
    if depth != []:
        w = max(depth) 
        GeometrySlab = t.select_box(((CornerMin.X(),CornerMin.Y(),storeys_dic[level_name]["minZ"]-w),\
                                 (CornerMax.X(),CornerMax.Y(),storeys_dic[level_name]["maxZ"]-H)),\
                                completely_within = True)
        for slab in IndicatedSlabs:
            if slab not in GeometrySlab:
                WrongElements.append (slab)
                
    if WrongElements != []:
        titel = "Checking elements on the floor {}".format(level_name)
        comment = "The element has an incorrect floor"
    
    for element in WrongElements:
        checking_elements.append ([element.ObjectType, element.GlobalId, titel, comment, element])
        CSVtable.append ([element.ObjectType, element.GlobalId, titel, comment])
            
    return checking_elements, CSVtable


    
def Space (m, Box, storeys_dic, Level_name,  checking_elements, CSVtable):
    '''
    Verification of the correspondence between the real and the indicated floor
    of the element

    Parameters
    ----------
    m : class 'ifcopenshell.file.file'
        Ifc File.
    Box : Bnd_Box
        box around the model from module ImportIFC.Model.ModelBox.
    storeys_dic : dict
        Structured information about floors from module ImportIFC.Model.Floors.
    Level_name : str
        name specified by the user.
    checking_elements : list
        the list for BCF to which the list with the error information will be added.
    CSVtable : list
        the list for CSV to which the list with the error information will be added.

    Returns
    -------
    checking_elements : list
        + [Type of element, GlobalID, Titel of issue, Comment for issue, IfcElement]
        e.g. [„IfcWall“, “1AWB_PzwPExQGFZX0DHwpa”, „Checking the properties IsExternal”,
              ”The property is not specified”,#138467 = IFCWALLSTANDARDCASE
              ('1AWB_PzwPExQGFZX0DHwpa', #1, 'Involucro 2497',...)].
    CSVtable : list
        Similar to a list, but without an IfcElement.
    '''

    CornerMax = Box.CornerMax()
    CornerMin = Box.CornerMin()

    X = [CornerMin.X()+i for i in range(int(round(CornerMax.X()-CornerMin.X())))]
    Y = [CornerMin.Y()+i for i in range(int(round(CornerMax.Y()-CornerMin.Y())))]
    Z = storeys_dic[Level_name]["minZ"] + 1.2

    points = [(x,y,Z) for x in X for y in Y]

    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_PYTHON_OPENCASCADE, True)

    walls = m.by_type("IfcWall")
    wall_b = {}
    for wall in walls:
        bbox = OCC.Core.Bnd.Bnd_Box()
        shape = ifcopenshell.geom.create_shape(settings, wall).geometry
        brepbndlib_Add (shape, bbox)
        wall_b[wall.GlobalId] = bbox
    
    tree_settings = ifcopenshell.geom.settings()
    tree_settings.set(tree_settings.DISABLE_OPENING_SUBTRACTIONS, True)
    t = ifcopenshell.geom.tree(m, tree_settings)

    point_without_space = []

    for point in points:
        elements = t.select(point)
        if all(not element.is_a("IfcSpace") for element in elements):
            if all(not element.is_a("IfcWall") for element in elements):
                if all(not element.is_a("IfcWall") for element in elements):
                    point_without_space.append(point)


    dX = gp_Dir()
    dY = gp_Dir(0,1,0)

    walls_without_space = []

    for point in point_without_space:
        coord = gp_Pnt(point[0],point[1],point[2])
        lX = gp_Lin(coord, dX)
        lY = gp_Lin(coord, dY)
        wX = {}
        wY = {}
        for key, value in wall_b.items():
            if not value.IsOut(lX):
                wX[key] = value.CornerMax().X()
            if not value.IsOut(lY):
                wY[key] = value.CornerMax().Y()
            
        if wX != {} and wY != {}:
        
            list_x = list(wX.items())
            list_x.sort(key=lambda i: i[1])
            left = []
            right = []
            for i in list_x:
                if point[0]>i[1]:
                    left.append(i)
                if point[0]<i[1]:
                    right.append(i)
        
            list_y = list(wY.items())
            list_y.sort(key=lambda i: i[1])
            bottom = []
            upper = []
            for i in list_y:
                if point[1]>i[1]:
                    bottom.append(i)
                if point[1]<i[1]:
                    upper.append(i)
                
            if left != [] and right != [] and bottom != [] and upper != []:
                walls_without_space.append([point, [left[-1][0], right[0][0], bottom[-1][0], upper[0][0]]])
        
    for i in walls_without_space:
        sorted(i[1])         

    Elements_for_Issues = []
    points_for_check = []

    for i in walls_without_space:
        if i[1] not in Elements_for_Issues:
            Elements_for_Issues.append(i[1])
            points_for_check.append(i[0])

    indexes_for_connection = []

    for point in points_for_check:
        if points_for_check.index(point)+1 < len(points_for_check):
            for i in range(points_for_check.index(point)+1,len(points_for_check)):
                elements = t.select_box((point,points_for_check[i]))

                if elements == []:
                    indexes_for_connection.append([points_for_check.index(point),i])

                else:
                    if all(not element.is_a("IfcSpace") for element in elements):
                        if all(not element.is_a("IfcWall") for element in elements):
                            if all(not element.is_a("IfcWall") for element in elements):
                                indexes_for_connection.append([points_for_check.index(point),i])

    indexes_for_connection_copy = indexes_for_connection

    for a in indexes_for_connection:
        index = indexes_for_connection.index(a)
        if index+1 < len(indexes_for_connection):
            for b in range(index+1, len(indexes_for_connection)):
                for c in a:
                    if c in indexes_for_connection[b]:
                        d = [e for e in indexes_for_connection_copy[b]\
                             if e not in indexes_for_connection_copy[index]] + indexes_for_connection_copy[index]
                        indexes_for_connection_copy[index] = d
                        indexes_for_connection_copy[b] = d
                    
    for_connection = []
    for i in indexes_for_connection_copy:
        if i not in for_connection:
            for_connection.append(i)
    

    Elements_End = []

    for i in for_connection:
        t = []
        for s in i:
            for f in Elements_for_Issues[s]:
                if f not in t:
                    t.append(f)
        Elements_End.append(t)

    for i in Elements_for_Issues:
        if Elements_for_Issues.index(i) not in sum(for_connection,[]):
            Elements_End.append(i)
            
    if Elements_End != []:
        titel = "Checking IfcSpace on the floor {}".format(Level_name)
        comment = "There is no IfcSpace between the walls"
    
    for element in Elements_End:
        elements = [m.by_guid(i) for i in element]        
        checking_elements.append (["IfcSpace", element, titel, comment, elements])
        CSVtable.append (["IfcSpace", element, titel, comment])
    
    return checking_elements, CSVtable
        
    
if __name__ == '__main__':
    import ImportIFC
    Model = ImportIFC.Model("D:\\M2\\Checker_Test\\Duplex_A.ifc")
    Box = Model.Box
    storeys_dic = Model.Floors()
    Level_name = "Level 2"
    checking_elements = []
    CSVtable = []
    a = Space(Model.m, Box, storeys_dic, Level_name,  checking_elements, CSVtable)
    print (a)
    
                


