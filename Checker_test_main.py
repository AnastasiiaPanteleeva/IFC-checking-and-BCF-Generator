# -*- coding: utf-8 -*-

######################################################################
#                                                                    #
# This is main file of IfcChecker                                    #
#                                                                    #
# It works with CSV, runs the necessary checks and saves the results #
#                                                                    #
######################################################################


from shutil import make_archive
from os import path
from PIL import Image
import csv
import os
import uuid
import pathlib
import datetime

#self-written modules
import CreateBCF
import Camera
import CheckerRules
import ImportIFC

'''
DATA REQUIRED FROM USER:
    Model (Path to File), Author (E-mail,that will be in the issue),
    Level_name (floor name for checking whether the elements are correctly
                linked to the floor and whether there is space)
'''
#specifies the location of the current file. If the model is in the same folder,
#then this is convenient
Path = pathlib.Path(__file__).parent.absolute()

Model = ImportIFC.Model("{}\\Duplex_A.ifc".format(Path))
#Model = ImportIFC.Model("{}\\20210125Prova.ifc".format(Path))
Level_name = "Level 2"
#Level_name = "P.T"
Author = "anastasiia.panteleeva@rwth-aachen.de"


Box = Model.Box
storeys_dic = Model.Floors()


#opening validation requirements in CSV and validating the model
with open('{}\\ifc_check.csv'.format(Path)) as checkfile:
    reader = csv.DictReader(checkfile,delimiter=";")

    CSVtable = [["Element","ID of element","Titel","Comment"]]
    checking_elements = []
    
    for row in reader:
        CheckerRules.CheckingProperty (row, Model.m, checking_elements, CSVtable)
        CheckerRules.CheckingElements (row, Model.m, checking_elements, CSVtable)
        CheckerRules.CheckingAttribute (row, Model.m, checking_elements, CSVtable)
    
    CheckerRules.Floor (Model.m, Box, storeys_dic, Level_name,  checking_elements, CSVtable)
    CheckerRules.Space (Model.m, Box, storeys_dic, Level_name,  checking_elements, CSVtable)


#saving results to a CSVtable    
with open('{}\\Results.csv'.format(Path), 'w') as testfile:
    csv_writer = csv.writer(testfile, delimiter=';')
    for element in CSVtable:
        csv_writer.writerow(element)


#saving results to a BCFzip
time = str(datetime.datetime.today().strftime("%Y-%m-%d_%H-%M-%S"))
os.mkdir("{}/Result_{}".format(Path,time))

for element in checking_elements:
    
    #create folders
    nummer = checking_elements.index(element)
    comment_folder = "{}/Result_{}/Comments{}_{}".format(Path,time, nummer,element[2])
    os.mkdir(comment_folder)    
        
    TopicGuid = str(uuid.uuid4())
    os.mkdir("{}/{}".format(comment_folder,TopicGuid))    

    #create BCF
    CreateBCF.createBCFversion("{}/bcf.version".format(comment_folder))
    
    ViewpointGuid = str(uuid.uuid4())
    
    CreateBCF.createViewpoint ("{}/{}/viewpoint.bcfv".format(comment_folder,TopicGuid), 
                               ViewpointGuid, element[1], Camera.Camera(element[4],Box),
                               Model.ElementsOnTheFloor(element[4]))
    
    CreateBCF.createMarkup("{}/{}/markup.bcf".format(comment_folder,TopicGuid), 
                           Model.IfcProject, element[1], TopicGuid, element[2], Author, element[3],
                           ViewpointGuid)
    
    image = Image.open("snapshot.png")
    image.save("{}/{}/snapshot.png".format(comment_folder,TopicGuid), "PNG")
    
    
    src = path.realpath("{}/bcf.version".format(comment_folder))
    root_dir,tail = path.split(src)
    make_archive("{}.bcfzip".format(comment_folder),"zip",root_dir)
      
    os.remove("{}\\bcf.version".format(comment_folder))
    os.remove("{}/{}/snapshot.png".format(comment_folder,TopicGuid)) 
    os.remove("{}\\{}\\viewpoint.bcfv".format(comment_folder,TopicGuid))
    os.remove("{}\\{}\\markup.bcf".format(comment_folder,TopicGuid))
    os.rmdir("{}\\{}".format(comment_folder,TopicGuid))
    os.rmdir(comment_folder)
