# -*- coding: utf-8 -*-


######################################################################
#                                                                    #
# This file is part of IfcChecker                                    #
#                                                                    #
# Camera module finds the coordinates of Direction, Up Vector and    #
# View Point                                                         #
#                                                                    #
######################################################################


import ifcopenshell
import ifcopenshell.geom
import OCC
from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Dir, gp_Lin
from OCC.Core.GeomAPI import GeomAPI_ProjectPointOnCurve
from OCC.Core.Geom import Geom_Curve, Geom_Line
import math


class Camera(object):
    
    
    def __init__(self, element, ModelBox):
        '''
        Parameters
        ----------
        element : class 'ifcopenshell.entity_instance.entity_instance'
            The selected element for the issue, the floor of which should
            be shown in the view.
        ModelBox : Bnd_Box
            box around the model from module ImportIFC.Model.ModelBox.
        '''
        self.Box = self._BoxOfView (element, ModelBox)
        
        CD = gp_Dir(1,1,-1)
        VCD = gp_Vec(CD)
        VCD.Normalized()
        self.CoordinatesDirection = (VCD.X(),VCD.Y(),VCD.Z())
        
        CD_1 = gp_Dir(1,1,2)
        VCD_1 = gp_Vec(CD_1)
        VCD_1.Normalized()
        self.CoordinatesUpVector = (VCD_1.X(),VCD_1.Y(),VCD_1.Z())

        self.CoordinatesViewPoint = self._GetViewPoint()

    
    def _BoxOfView (self, element, ModelBox):
        '''
        Create a box around the element. If the element has no geometry or
        is missing, the general model box will be used

        Parameters
        ----------
        element : class 'ifcopenshell.entity_instance.entity_instance'
            The selected element for the issue, the floor of which should
            be shown in the view.
        ModelBox : Bnd_Box
            box around the model from module ImportIFC.Model.ModelBox.

        Returns
        -------
        bbox : Bnd_Box
            The box used for setting the camera.
        '''
        if element != "":
            if type(element)==list:
                shape = self._CreateShape(element)
                bbox = self._CreateBox(shape)
            else:            
                if hasattr(element,"Representation"):
                    shape = self._CreateShape(element)
                    bbox = self._CreateBox(shape)
                else:
                    bbox = ModelBox
        if element == "":
            bbox = ModelBox
        return bbox

        
    def _GetViewPoint(self):
        '''The calculation of the coordinates of the camera'''
        
        Center = self._Center(self.Box)
        MaxPoint = self._MaxPoint(self.Box)
        MinPoint = self._MinPoint(self.Box)
        
        Point_1 = gp_Pnt(MinPoint.X(),MinPoint.Y(),Center.Z())
        Point_2 = gp_Pnt(MaxPoint.X(),MinPoint.Y(),Center.Z())
        Point_3 = gp_Pnt(MinPoint.X(),MaxPoint.Y(),Center.Z())
        Vector_1 = gp_Vec(Point_2,Point_1)
        Vector_2 = gp_Vec(Point_2,Point_3)
        Angle = Vector_1.Angle(Vector_2)
        if Angle <= math.pi/4:
            Point = gp_Pnt(MaxPoint.X(),MinPoint.Y(),MaxPoint.Z())
        else:
            Point = gp_Pnt(MinPoint.X(),MaxPoint.Y(),MaxPoint.Z())
        
        direction_axe = gp_Dir(1,1,-1)
        Axe = gp_Lin(Center, direction_axe)
        Axe_Curve = Geom_Line(Axe)
        Project_1 = GeomAPI_ProjectPointOnCurve(Point, Axe_Curve)
        index = Project_1.NbPoints()
        Axe_point = Project_1.Point(index)
        
        direction_horizon = gp_Dir(1,-1,0)
        Axe_horizon = gp_Lin(Axe_point, direction_horizon)
        Axe_Curve_horizon = Geom_Line(Axe_horizon)
        Project_2 = GeomAPI_ProjectPointOnCurve(Point, Axe_Curve_horizon)
        index = Project_2.NbPoints()
        Axe_point_horizon = Project_2.Point(index)
        
        SizeElement = gp_Pnt.Distance(Axe_point,Axe_point_horizon)
       #Distance = SizeElement/math.tan(math.pi/6) + gp_Pnt.Distance(Axe_point, Center)
        
        h = gp_Pnt.Distance(Point, Axe_point_horizon)
        if h/SizeElement > 1.5/2 :
            SizeElement = 2 * h / 1.5           
            
        Distance = SizeElement/math.tan(math.pi/6) + gp_Pnt.Distance(Axe_point, Center)

        Vector = gp_Vec(self.CoordinatesDirection[0],self.CoordinatesDirection[1],self.CoordinatesDirection[2])
        Vector.Reverse()
        Vector.Scale(Distance)
        ViewPoint = Center.Translated(Vector)
        Coordinates = (ViewPoint.X(),ViewPoint.Y(),ViewPoint.Z())
               
        return Coordinates

        
    def _CreateShape(self, element):
        settings = ifcopenshell.geom.settings()
        settings.set(settings.USE_PYTHON_OPENCASCADE, True)
        if type(element)==list:
            shape = []
            for el in element:
                sh = ifcopenshell.geom.create_shape (settings,el).geometry
                shape.append(sh)
        else:
            shape = ifcopenshell.geom.create_shape (settings,element).geometry
        return shape

        
    def _CreateBox(self, shape):
        bbox = OCC.Core.Bnd.Bnd_Box()
        if type(shape)==list:
            for i in shape:
                brepbndlib_Add (i, bbox)
        else:
            brepbndlib_Add (shape, bbox)
        return bbox

        
    def _Center(self, bbox):
        box_center = ifcopenshell.geom.utils.get_bounding_box_center(bbox)
        return box_center

    
    def _MaxPoint(self, bbox):
        return bbox.CornerMax()

    
    def _MinPoint(self, bbox):
        return bbox.CornerMin()

                
        
if __name__ == '__main__':
    m = ifcopenshell.open("D:\\M2\\Checker_Test\\Duplex_A.ifc")
    element = m.by_guid('2O2Fr$t4X7Zf8NOew3FLPP')
    camera = Camera(element, m)
    print (camera.CoordinatesViewPoint)
