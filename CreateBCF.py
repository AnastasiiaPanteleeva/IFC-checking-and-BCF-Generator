# -*- coding: utf-8 -*-

######################################################################
#                                                                    #
# This file is part of IfcChecker                                    #
#                                                                    #
# CreateBCF module has function for creating BCF format              #
#                                                                    #
######################################################################


import xml.etree.ElementTree as xml
import uuid
import datetime

def createBCFversion(filename):
    '''
    Creating bcf.version

    Parameters
    ----------
    filename : str
        Name of file with location.
    '''
    root = xml.Element("Version")
    root.set("VersionId","2.0")
    root.set("xsi:noNamespaceSchemaLocation","version.xsd")
    root.set("xmlns:xsi","http://www.w3.org/2001/XMLSchema-instance")
    leaf = xml.SubElement(root,"DetailedVersion")
    leaf.text = "2.0 RC"
    tree = xml.ElementTree(root)
    tree.write(filename, method='xml', encoding = "UTF-8", xml_declaration = True)


def createMarkup(filename, IfcProject, IfcSpatialStructureElement, TopicGuid, 
                 Titel, Author, Comment, ViewpointGuid):
    '''
    Creating markup.bcf

    Parameters
    ----------
    filename : str
        Name of file with location.
    IfcProject : str
        GlobalId of IfcProject.
    IfcSpatialStructureElement : str
        GlobalId of elemnt for issue.
    TopicGuid : str
        Id (uuid) of topic.
    Titel : str
        Titel of issue.
    Author : str
        E-mail,that will be in the issue.
    Comment : str
        Comment for issue.
    ViewpointGuid : str
        Id (uuid) of View.
    '''    
    markup = xml.Element("Markup")
    
    header = xml.SubElement(markup,"Header")
    file = xml.SubElement(header,"File")
    file.set("IfcProject",IfcProject)
    if IfcSpatialStructureElement != "":
        if type(IfcSpatialStructureElement)==list:
            for i in IfcSpatialStructureElement:
                file.set("IfcSpatialStructureElement",i)
        else:
            file.set("IfcSpatialStructureElement",IfcSpatialStructureElement)
    file.set("isExternal","true")
    
    topic = xml.SubElement(markup,"Topic")
    topic.set("Guid", TopicGuid)
    topic.set("TopicType", "Error")
    topic.set("TopicStatus", "Open")
    title = xml.SubElement(topic,"Title")
    title.text = Titel
    Priority = xml.SubElement(topic,"Priority")
    Priority.text = "Normal"
    CreationDate = xml.SubElement(topic,"CreationDate")
    CreationDate.text = datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%S")
    CreationAuthor = xml.SubElement(topic,"CreationAuthor")
    CreationAuthor.text = Author
    ModifiedDate = xml.SubElement(topic,"ModifiedDate")
    ModifiedDate.text = datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%S")
    ModifiedAuthor = xml.SubElement(topic,"ModifiedAuthor")
    ModifiedAuthor.text = Author
    
    comment = xml.SubElement(markup,"Comment")
    CommentGuid = uuid.uuid4()
    comment.set("Guid", str(CommentGuid))
    date = xml.SubElement(comment,"Date")
    date.text = datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%S")
    CommentAuthor = xml.SubElement(comment,"Author")
    CommentAuthor.text = Author
    CommentComment = xml.SubElement(comment,"Comment")
    CommentComment.text = Comment
    CommentTopic = xml.SubElement(comment,"Topic")
    CommentTopic.set("Guid", TopicGuid)
    Viewpoint = xml.SubElement(comment,"Viewpoint")
    Viewpoint.set("Guid", ViewpointGuid)
    ModifiedDate_c = xml.SubElement(comment,"ModifiedDate")
    ModifiedDate_c.text = datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%S")
    ModifiedAuthor_c = xml.SubElement(comment,"ModifiedAuthor")
    ModifiedAuthor_c.text = Author
    
    viewpoints = xml.SubElement(markup,"Viewpoints")
    viewpoints.set("Guid", ViewpointGuid)
    viewpoint_ = xml.SubElement(viewpoints,"Viewpoint")
    viewpoint_.text = "viewpoint.bcfv"
    Snapshot = xml.SubElement(viewpoints,"Snapshot")
    Snapshot.text = "snapshot.png"
        
    tree = xml.ElementTree(markup)
    tree.write(filename, method='xml', encoding = "UTF-8", xml_declaration = True)

    
def createViewpoint (filename,ViewpointGuid,ElementId, Camera, ElementsIdFloor):
    '''
    Creating viewpoint.bcfv 

    Parameters
    ----------
    filename : str
        Name of file with location.
    ViewpointGuid : str
        Id (uuid) of View.
    ElementId : str
        GlobalId of elemnt for issue.
    Camera : class
        class from module Camera, which has coordinates of view point, direction
        and up vector.
    ElementsIdFloor : list
        List of floor element IDs (str) from module ImportIFC.ElementsOnTheFloor.
    '''
    
    CoordinatesViewPoint = Camera.CoordinatesViewPoint
    CoordinatesDirection = Camera.CoordinatesDirection
    CoordinatesUpVector = Camera.CoordinatesUpVector
    
    VisualizationInfo = xml.Element("VisualizationInfo")
    VisualizationInfo.set("Guid", ViewpointGuid)    
    components = xml.SubElement(VisualizationInfo,"Components")
    ViewSetupHints = xml.SubElement(components,"ViewSetupHints")
    ViewSetupHints.set("SpacesVisible","false")
    ViewSetupHints.set("SpaceBoundariesVisible","false")
    ViewSetupHints.set("OpeningsVisible","false")
    if ElementId != "":
        Selection = xml.SubElement(components,"Selection")        
        if type(ElementId)==list:
            for ids in ElementId:
                Component = xml.SubElement(Selection,"Component")
                Component.set("IfcGuid",ids)
        else:
            Component = xml.SubElement(Selection,"Component")
            Component.set("IfcGuid",ElementId)
        Visibility = xml.SubElement(components,"Visibility")
        Visibility.set("DefaultVisibility","false")
        Exceptions = xml.SubElement(Visibility,"Exceptions")
        for ID in ElementsIdFloor:
            ComponentV = xml.SubElement(Exceptions,"Component")
            ComponentV.set("IfcGuid",ID)
    else:
        Visibility = xml.SubElement(components,"Visibility")
        Visibility.set("DefaultVisibility","true")
        
    PerspectiveCamera = xml.SubElement(VisualizationInfo,"PerspectiveCamera")
    
    CameraViewPoint = xml.SubElement(PerspectiveCamera,"CameraViewPoint")
    CameraViewPoint_X = xml.SubElement(CameraViewPoint,"X")
    CameraViewPoint_X.text = str(CoordinatesViewPoint[0])
    CameraViewPoint_Y = xml.SubElement(CameraViewPoint,"Y")
    CameraViewPoint_Y.text = str(CoordinatesViewPoint[1])
    CameraViewPoint_Z = xml.SubElement(CameraViewPoint,"Z")
    CameraViewPoint_Z.text = str(CoordinatesViewPoint[2])
    
    CameraDirection = xml.SubElement(PerspectiveCamera,"CameraDirection")
    CameraDirection_X = xml.SubElement(CameraDirection,"X")
    CameraDirection_X.text = str(CoordinatesDirection[0])
    CameraDirection_Y = xml.SubElement(CameraDirection,"Y")
    CameraDirection_Y.text = str(CoordinatesDirection[1])
    CameraDirection_Z = xml.SubElement(CameraDirection,"Z")
    CameraDirection_Z.text = str(CoordinatesDirection[2])
    
    CameraUpVector = xml.SubElement(PerspectiveCamera,"CameraUpVector")
    CameraUpVector_X = xml.SubElement(CameraUpVector,"X")
    CameraUpVector_X.text = str(CoordinatesUpVector[0])
    CameraUpVector_Y = xml.SubElement(CameraUpVector,"Y")
    CameraUpVector_Y.text = str(CoordinatesUpVector[1])
    CameraUpVector_Z = xml.SubElement(CameraUpVector,"Z")
    CameraUpVector_Z.text = str(CoordinatesUpVector[2])
    
    FieldOfView = xml.SubElement(PerspectiveCamera,"FieldOfView")
    FieldOfView.text = "60.0"
    
    tree = xml.ElementTree(VisualizationInfo)
    tree.write(filename, method='xml', encoding = "UTF-8", xml_declaration = True)    
    
    
if __name__ == "__main__":
    createBCFversion("bcf.version")
    createMarkup("markup.bcf", "IfcProject", "IfcSpatialStructureElement", "TopicGuid", 
                 "Titel", "Author", "Comment", "bcfv")


