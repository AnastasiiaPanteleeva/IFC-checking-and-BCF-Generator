# IFC-checking and BCF-Generator
![the scheme of work](images/1.Programm.png)
In this project 5 types of checkings were developed that check elements, properties, attributes, elements on the floor and the presence of spaces between the walls. The result is formatted as a BCF. For the BCF format, an algorithm was prescribed for automatically determining the camera position and view settings, which provides better feedback.

## IFC-checking

![1 Check](https://github.com/AnastasiiaPanteleeva/IFC-checking-and-BCF-Generator/blob/117fe58e20d09b81398104a76ce91f1264210031/images/1.Checking%20elements.png)
![2 Check](https://github.com/AnastasiiaPanteleeva/IFC-checking-and-BCF-Generator/blob/79e668b4e14ed9a18a5fc64df99e27a8840c4064/images/2.Checking%20properties.png)
![3 Check](https://github.com/AnastasiiaPanteleeva/IFC-checking-and-BCF-Generator/blob/117fe58e20d09b81398104a76ce91f1264210031/images/3.Checking%20attributes.png)
![4 Check](https://github.com/AnastasiiaPanteleeva/IFC-checking-and-BCF-Generator/blob/117fe58e20d09b81398104a76ce91f1264210031/images/4.Checking%20floors.png)
![5 Check](https://github.com/AnastasiiaPanteleeva/IFC-checking-and-BCF-Generator/blob/117fe58e20d09b81398104a76ce91f1264210031/images/5.Checking%20spaces.png)

## Calculation of camera coordinates for BCF format

- determining the dimensions of an element or model
![Model Box](https://github.com/AnastasiiaPanteleeva/IFC-checking-and-BCF-Generator/blob/45bf869c8f15e76b7e2a47bd0a05aef0cc3529f9/images/6.Model%20Box.png)
- finding the closest point to the edge of the frame
![Point](https://github.com/AnastasiiaPanteleeva/IFC-checking-and-BCF-Generator/blob/45bf869c8f15e76b7e2a47bd0a05aef0cc3529f9/images/7.Point.png)
- calculation of the distance from the center of the object to the camera, thereby determining its coordinates
![Camera](https://github.com/AnastasiiaPanteleeva/IFC-checking-and-BCF-Generator/blob/45bf869c8f15e76b7e2a47bd0a05aef0cc3529f9/images/8.Camera.png)
