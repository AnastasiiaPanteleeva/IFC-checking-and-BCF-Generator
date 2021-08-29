# -*- coding: utf-8 -*-

######################################################################
#                                                                    #
# This file is part of IfcChecker                                    #
#                                                                    #
# ImportIFC module loads the IFC file, determines its endpoints,     #
# floor structure and floor elements.                                #
#                                                                    #
######################################################################


import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util
import ifcopenshell.util.selector
import OCC
from OCC.Core.BRepBndLib import brepbndlib_Add


class Model(object):
    
    
    def __init__(self, path_model):
        '''
        Parameters
        ----------
        path_model : str
            IFC File location.
        '''
        self.m = ifcopenshell.open(path_model)
        self.IfcProject = str(self.m.by_type("IfcProject")[0].GlobalId)
        self.Box = self.ModelBox()
 
        
    def ModelBox(self):
        '''
        Creating a box around the model to determine its dimensions
        
        Returns
        ----------
        Bnd_Box        
        '''
        settings = ifcopenshell.geom.settings()
        settings.set(settings.USE_PYTHON_OPENCASCADE, True)
        elements = self.m.by_type("IfcProduct")
        bbox = OCC.Core.Bnd.Bnd_Box()
        for element in elements:
            if element.is_a("IfcOpeningElement"): continue
            if element.Representation:
                shape = ifcopenshell.geom.create_shape(settings, element).geometry
                brepbndlib_Add (shape, bbox)
        return bbox
    

    def ElementsOnTheFloor (self, element):        
        '''
        Parameters
        ----------
        element : class 'ifcopenshell.entity_instance.entity_instance'
            The selected element for the issue, the floor of which should
            be shown in the view.
            
        Returns
        -------
        ElementsIdFloor : list
            List of floor element IDs (str).
        '''        
        if type(element)==list:
            element = element[0]
        
        if element != "" and hasattr(element,"Representation"):
            
            if element.is_a('IfcFurnishingElement'):
                for i in element.ContainedInStructure:
                    if i.is_a('IfcRelContainedInSpatialStructure'):
                        for agg in i.RelatingStructure.Decomposes:
                            if agg.is_a('IfcRelAggregates'):
                                StoreyId = agg.RelatingObject.GlobalId
            else:
                for Structure in element.ContainedInStructure:
                    if Structure.RelatingStructure.is_a("IfcBuildingStorey"):
                        StoreyId = Structure.RelatingStructure.GlobalId
            
            elements = ifcopenshell.util.selector.Selector().parse(self.m ,'@ #{}'.format(StoreyId))

            #Furniture
            level = self.m.by_guid(StoreyId)
            for agg in level.IsDecomposedBy:
                if agg.is_a("IfcRelAggregates"):
                    spaces = agg.RelatedObjects
                    for s in spaces:
                        for i in s.ContainsElements:
                            if i.is_a("IfcRelContainedInSpatialStructure"):
                                for element in i.RelatedElements:
                                    elements.append(element)
                                    
            if not element.is_a("IfcCovering"):                    
                for i in elements:
                    if i.is_a("IfcCovering"):
                        elements.remove(i)
                for i in elements:
                    if i.is_a("IfcCovering"):
                        elements.remove(i)        
                    
            ElementsIdFloor = []
            for i in elements:
                ElementsIdFloor.append(i.GlobalId)
            return ElementsIdFloor                    

    
    def Floors (self):
        '''
        Defining the order of floors and their heights
        
        Returns
        -------
        storeys_dic : dict
            e.g. {'T/FDN': {'minZ': -1.25, 'maxZ': 0.0, 'GlobalId':
                '1xS3BCk291UvhgP2dvNsgp','Index': 0}, 'Level 1': {}...}
        '''
        storeys = self.m.by_type("IfcBuildingStorey") #selecting all levels
        storeys_with_height = []
        for storey in storeys:
            #the lower level floor
            storeys_with_height.append([storey.Name, storey.GlobalId, storey.Elevation])
             #sorting floors [['T/FDN', -1.25], ['Level 1', 0.0]...
        storeys_with_height.sort(key=lambda Storey:Storey[2])
        #upper floor mark - lower mark of the next floor
        for i in range(len(storeys_with_height)-1):
            storeys_with_height[i].append(storeys_with_height[i+1][2])
            # the last floor has an upper coordinates from the box
            storeys_with_height[-1].append(self.Box.CornerMax().Z())

        storeys_dic = {i[0]:{"minZ":i[2],"maxZ":i[3],"GlobalId":i[1], "Index":storeys_with_height.index(i)}\
                       for i in storeys_with_height}
        return storeys_dic

                   
if __name__ == '__main__':
    model = Model("D:\\M2\\Checker_Test\\Duplex_A.ifc")
    print (model.Floors())
    
    
                    
                
                
        
        