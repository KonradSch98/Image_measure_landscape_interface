import numpy as np
import glob


#local import
from shoelace import shoelace



#################################################################################



class LineBuilder:
    

    def __init__(self, back_image ,can , list: list, fpath: str , color):
        """
        This algorithm handles a mouseclick event in an matplotlib environment.
        A point is marked at the clicked coordinates,
        the given points are stored in a vector and connected pairwise in order by lines
        forming and closing a polygon.
        One shape is closed when the very first point is clicked again.
        Shapes are then also stored in a dict.
    
        
        Args:
            back_image ():  the canvas background image on which the users marks the shapes, as mpl data
                            e.g.: mpl_can.ax.imshow(self.image_data)
            ax ():          a defined axis object in matplotlib environment
            list (list):    a global list variable used to display the coordinates of the clicked points in the Gui
            fpath (str):   the file path of the background_image. Is used to load the image_specific extra stored meta data from a .txt
                            e.g.: 'C:/Users/admin/Desktop/test.jpg'
            color (str):    color of the dots/lines 
                            e.g.: 'red'
                        
        """

        self.list = list
        self.image = back_image
        self.fpath = fpath
        self.ax = can.ax
        self.can = can
        self.color = color

        self.xs = []                                        #point x-coord
        self.ys = []                                        #point y-coord
        self.cid = back_image.figure.canvas.mpl_connect('button_press_event', self)
        #pan_handler = panhandler(back_image.figure)
        self.p_counter = 0                                  #point counter
        self.shape_counter = 0                              #counter for different closed shapes
        self.shape = {}                                     #dictionary of closed shapes
        self.precision = 0                                  #precision to distinguish betw. last clicked point towards first point






    def __call__(self, event):
        """
        mouseclick event handler function
        handles what happens when the user clicks on the image

        Args:
            event (_type_): _description_

        """



        if event.button == 1 and self.can.toolbar.mode != 'pan/zoom':
            
            self.precision = (self.ax.get_ylim()[0]-self.ax.get_ylim()[1]) / 40
            
            if event.inaxes!=self.image.axes: 
                return            #?
            
            ## add first point in shape
            if self.p_counter == 0:           
                self.xs.append(event.xdata)
                self.ys.append(event.ydata)
                self.list.addItem('Shape ' + str( self.shape_counter + 1))
            
            ## closes one shape and starts a new one
            if np.abs(event.xdata-self.xs[0])<=self.precision and np.abs(event.ydata-self.ys[0])<=self.precision and self.p_counter != 0:
                self.xs.append(self.xs[0])              
                self.ys.append(self.ys[0])
                self.list.addItem(str(self.p_counter) +":    x" + str(int(self.xs[self.p_counter])) + "     y:"+str(int(self.ys[self.p_counter])))
                
                self.ax.text(self.xs[0]+100, self.ys[0]-100, self.p_counter, fontsize=10, color="red")  #index point label in image
                self.ax.plot(self.xs,self.ys,color=self.color)          #plots line from .. to ..
                self.image.figure.canvas.draw()                    #show
                self.shape[self.shape_counter] = [self.xs,self.ys]      #store shape            
                
                

                #calculate pixel space of polygon
                self.pixel_space = shoelace(self.shape[self.shape_counter])
                
                #load image spec. info and calculate real space
                self.fname = self.fpath.split('/')[-1]
                img_paths = glob.glob(f'{self.fpath.rstrip("/").replace(self.fname, "")}' + self.fname[:8] +'*.txt')
                size_file = open(img_paths[0], 'r')
                lines = size_file.readlines()
                size_file.close()
                
                #size calculations
                shape_size = float(lines[0]) * self.pixel_space
                ax1 = np.sqrt(float(lines[1])**2 * (self.xs[1]-self.xs[0])**2 + float(lines[2])**2 * (self.ys[1]-self.ys[0])**2)
                ax2 = np.sqrt(float(lines[1])**2 * (self.xs[2]-self.xs[1])**2 + float(lines[2])**2 *(self.ys[2]-self.ys[1])**2)
                
                
                self.list.addItem('Shape size:    ' + str("{:.3f}".format(shape_size)) + 'qm')
                self.list.addItem('Ax1:    ' + str("{:.3f}".format( ax1 )) + 'm')
                self.list.addItem('Ax1:    ' + str("{:.3f}".format( ax2 )) + 'm')
                self.list.addItem('' )

                #reset
                self.xs = []
                self.ys = []
                self.p_counter = 0
                self.shape_counter = self.shape_counter + 1
                
            #set every other point
            else:
                if self.p_counter != 0:
                    self.xs.append(event.xdata)
                    self.ys.append(event.ydata)
                self.ax.scatter(self.xs,self.ys,s=60,color=self.color)          #plot clicked point
                self.ax.plot(self.xs,self.ys,color=self.color)                  #plot line betw points
                self.ax.text(self.xs[self.p_counter]+100, self.ys[self.p_counter]+100, self.p_counter, fontsize=10, color="red")
                self.image.figure.canvas.draw()
                self.list.addItem(str(self.p_counter) +":    x" + str(int(self.xs[self.p_counter])) + "     y:"+str(int(self.ys[self.p_counter])))
                self.p_counter = self.p_counter + 1
        
        