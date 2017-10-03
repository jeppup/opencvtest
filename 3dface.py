import numpy as np
import cv2
import vtk
import interpolation as injter

class KeyboardInterface(object):
    """Keyboard interface.

    Provides a simple keyboard interface for interaction. You should
    extend this interface with keyboard shortcuts for changing the
    isovalue interactively.

    """

    def __init__(self, contour):
        self.screenshot_counter = 0
        self.render_window = None
        self.window2image_filter = None
        self.png_writer = None
        self.contours = contour
        self.currentContourValue = 0.0
        # Add the extra attributes you need here...

    def keypress(self, obj, event):
        """This function captures keypress events and defines actions for
        keyboard shortcuts."""
        key = obj.GetKeySym()
        numberOfContours = self.contours.GetNumberOfContours()
        if key == "9":
            self.render_window.Render()
            self.window2image_filter.Modified()
            screenshot_filename = ("screenshot%02d.png" %
                                   (self.screenshot_counter))
            self.png_writer.SetFileName(screenshot_filename)
            self.png_writer.Write()
            print("Saved %s" % (screenshot_filename))
            self.screenshot_counter += 1
        elif key == "Up":
            self.currentContourValue += 0.02
            for i in range(0, numberOfContours - 1):
                self.contours.SetValue(i, self.currentContourValue)
            self.render_window.Render()
            print(self.currentContourValue)
        elif key == "Down":
            self.currentContourValue -= 0.02
            for i in range(0, numberOfContours - 1):
                self.contours.SetValue(i, self.currentContourValue)
            self.render_window.Render()
            print(self.currentContourValue)



def shift_laplace(laplacian_img):
    min = 0
    max = 0
    for i in range(0, len(laplacian_img)):
        for j in range(0, len(laplacian_img[i])):
            val = laplacian_img[i][j]
            if val > max:
                max = val
            if val < min:
                min = val

    max = max + np.absolute(min)
    for i in range(0, len(laplacian_img)):
        for j in range(0, len(laplacian_img[i])):
            val = laplacian_img[i][j]
            new_val = (val + np.absolute(min))/max
            laplacian_img[i][j] = new_val
            #print('old val:' + str(val) + ', new val:' + str(new_val))
    return laplacian_img

def create_vtk_dataset(img, gradient_map):
    points = vtk.vtkPoints()
    for i in range(0, len(img)):
        for j in range(0, len(img[i])):
            points.InsertNextPoint(i, j/1000, gradient_map[i][j])
    return points

def create_vtk_structureddataset(img, gradient_map):
    dx = 0.1
    grid = vtk.vtkImageData()
    grid.SetOrigin(0,0,0)
    grid.SetSpacing(dx,dx,dx)
    grid.SetDimensions(len(img), len(img[0]), 1)

    array = vtk.vtkDoubleArray()
    array.SetNumberOfComponents(1)
    array.SetNumberOfTuples(grid.GetNumberOfPoints())
    idx = 0
    for i in range(0,len(gradient_map)):
        for j in range(0,len(gradient_map[i])):
            array.SetValue(idx, gradient_map[i][j])
            idx = idx + 1

    grid.GetPointData().AddArray(array)
    return grid


data = np.random.rand(20)
injter.interpolate(data, 1000)

file_name = 'face.jpg'
img = cv2.imread(file_name)
img2gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imshow('img', img)
cv2.waitKey()
img_laplace = cv2.Laplacian(img2gray, cv2.CV_64F)
cv2.imshow('img', img_laplace)
cv2.waitKey()

shifted = shift_laplace(img_laplace)
cv2.imshow('img', shifted)
cv2.waitKey()


##### VTK CRAP
data = create_vtk_structureddataset(img, img_laplace)


a = -500
b = 100
iss = vtk.vtkImageShiftScale()
iss.SetInputData(data)
#iss.SetOutputScalarTypeToUnsignedChar()
#iss.SetShift(-a)
#iss.SetScale(255.0/(b-a))
#
# Now you use iss.GetOutput() instead

# create an outline of the dataset
outline = vtk.vtkOutlineFilter()
outline.SetInputData(data)
outlineMapper = vtk.vtkPolyDataMapper()
outlineMapper.SetInputConnection( outline.GetOutputPort() )
outlineActor = vtk.vtkActor()
outlineActor.SetMapper( outlineMapper )


# the actors property defines color, shading, line width,...
outlineActor.GetProperty().SetColor(0.0,0.0,1.0)
outlineActor.GetProperty().SetLineWidth(2.0)






#
# add your code here...
opacityTransferFunction = vtk.vtkPiecewiseFunction()
opacityTransferFunction.AddPoint(20, 0.0)
opacityTransferFunction.AddPoint(255, 0.5)


# Create transfer mapping scalar value to color
colorTransferFunction = vtk.vtkColorTransferFunction()
colorTransferFunction.AddRGBPoint(0.0, 0.0, 0.0, 0.0)
colorTransferFunction.AddRGBPoint(64.0, 1.0, 0.0, 0.0)
colorTransferFunction.AddRGBPoint(128.0, 0.8, 0.8, 0.8)
colorTransferFunction.AddRGBPoint(192.0, 0.9, 0.9, 0.9)
colorTransferFunction.AddRGBPoint(255.0, 1.0, 1.0, 1.0)

# The property describes how the data will look
volumeProperty = vtk.vtkVolumeProperty()
volumeProperty.SetColor(colorTransferFunction)
#volumeProperty.SetScalarOpacity(opacityTransferFunction)
volumeProperty.SetGradientOpacity(opacityTransferFunction)


volumeProperty.ShadeOn()
volumeProperty.SetInterpolationTypeToLinear()

# The mapper / ray cast function know how to render the data
compositeFunction = vtk.vtkVolumeRayCastCompositeFunction()
mipFunction = vtk.vtkVolumeRayCastMIPFunction()
volumeMapper = vtk.vtkVolumeRayCastMapper()
volumeMapper.SetVolumeRayCastFunction(compositeFunction)
volumeMapper.SetInputConnection(iss.GetOutputPort())

# The volume holds the mapper and the property and
# can be used to position/orient the volume
volume = vtk.vtkVolume()
volume.SetMapper(volumeMapper)
volume.SetProperty(volumeProperty)


#
# transfer functions,
# vtkVolumeProperty,
# vtkVolumeRayCastMapper,
# vtkVolumeRayCastFunction,
# vtkVolume, ...
#






# a text actor
textActor = vtk.vtkTextActor()
tp = vtk.vtkTextProperty()
tp.BoldOn()
tp.ShadowOn()
tp.ItalicOn()
tp.SetColor(0,0,0)
tp.SetFontFamilyToArial()
tp.SetFontSize(30)
textActor.SetTextProperty(tp)
tpc = textActor.GetPositionCoordinate()
tpc.SetCoordinateSystemToNormalizedViewport()
tpc.SetValue(0.1,0.9)
textActor.SetWidth(.2)
textActor.SetHeight(.2)
textActor.SetInput( "File: " + file_name )

# renderer and render window
ren = vtk.vtkRenderer()
ren.SetBackground(1, 1, 1)
renWin = vtk.vtkRenderWindow()
renWin.SetSize( 512, 512 )
renWin.AddRenderer( ren )

# render window interactor
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow( renWin )

# add the actors
ren.AddActor( outlineActor )
ren.AddActor( textActor )
ren.AddVolume(volume)
renWin.Render()

# create window to image filter to get the window to an image
w2if = vtk.vtkWindowToImageFilter()
w2if.SetInput(renWin)

# create png writer
wr = vtk.vtkPNGWriter()
wr.SetInputConnection(w2if.GetOutputPort())

# Python function for the keyboard interface
# count is a screenshot counter
count = 0
def Keypress(obj, event):
    global count, iv
    key = obj.GetKeySym()
    if key == "s":
        renWin.Render()
        w2if.Modified() # tell the w2if that it should update
        fnm = "screenshot%02d.png" %(count)
        wr.SetFileName(fnm)
        wr.Write()
        print("Saved '%s'" %(fnm))
        count = count+1
    # add your keyboard interface here
    # elif key == ...

# add keyboard interface, initialize, and start the interactor
iren.AddObserver("KeyPressEvent", Keypress)
iren.Initialize()
iren.Start()

