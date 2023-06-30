from PyQt5 import QtWidgets as QtW
from PyQt5 import QtGui as QtG
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
import cv2
from pathlib import Path
from mpl_interactions import zoom_factory

#local import
from LineBuilder import LineBuilder




#################################################################################





class Mpl_QtWidget(QtW.QWidget):

    

    def __init__(self, parent=None):
        """
        Class for the mpl canvas IN the Qt environment
        """
        
    
        super().__init__(parent)

        global fig
        fig = Figure()
        
        self.can = FigureCanvasQTAgg(fig)                       #define mpl canvas
        self.toolbar = NavigationToolbar2QT(self.can, self)     #define mpl toolbar   ???
        #self.toolbar.remove_tool
        layout = QtW.QVBoxLayout(self)                          #set vertcical widget layout 
        layout.addWidget(self.toolbar)                          # ?? only for toolbar ???
        layout.addWidget(self.can)                              #define canvas as widget 

        self.ax = self.can.figure.add_subplot(111)              #define fig on canvas




#################################################################################




class MyListwidget(QtW.QListWidget):
    """
    defining my list widget
    primarily here to include the clipboard function
    """

    
    def keyPressEvent(self, event):
        if event.matches(QtG.QKeySequence.Copy):
            
            ClipBoard = QtW.QApplication.clipboard()
            ClipBoard.clear(mode=ClipBoard.Clipboard)
            values = []
            for item in self.selectedIndexes():
                values.append(item.data())
            ClipBoard.setText("\n".join(values),mode=ClipBoard.Clipboard)
            
        


#################################################################################



class MyQtApp(QtW.QWidget):
    

    def __init__(self):
        """

        Class of my GUI window allowing the user to load/show an image
        upon which can mark points and close shapes
        which coordinates are displayed on the right side
        
        The measure function needs a .txt file in the image dir
        carying the image_name in its filename
        like 'G0010183_undist_size.txt' for the G0010183.jpg file.
        with content lines eg:
        
        0.0009342020206599135
        0.030559537531835428
        0.03056990046680869
        
        being the space size of a pixel, its x-size and y-size each in meter
        So to say the space one pixel represents in real world  

        ######
        
        
        Sets the layout of the GUI
        """
        
        

        super(MyQtApp, self).__init__()

        global LIST                                                          #define list widget to display points coordinates
        self.path = None                                                     #set path variable
        self.brows_or_dir = None

        #elements
        self.mpl_can = Mpl_QtWidget(self)                                    #import my canvas widget
        self.mpl_can.setSizePolicy(QtW.QSizePolicy.Expanding, QtW.QSizePolicy.Expanding)
        #button to load image to canvas
        self.btn_load = QtW.QPushButton('Show Image', clicked = self.load_image)      
        #button for file browser
        self.btn_file_dial = QtW.QPushButton("Browse File", clicked=self.getfile )                     
        self.btn_copy = QtW.QPushButton("Copy", clicked = self.CopyClipboard)
        
        self.can_titel = QtW.QLabel()                                        #a titel element
        self.can_titel.setText('Click to include shape markers. Mark points counter clock-wise. 150 pixel precision to close the shape.')
        self.can_titel.setAlignment(Qt.AlignCenter)
        self.can_titel.setFont(QtG.QFont('Arial', 10))
        self.can_titel.setSizePolicy(QtW.QSizePolicy.Fixed, QtW.QSizePolicy.Fixed)  #set label to fixed size always
        self.can_titel.setFixedHeight(40)
        
        LIST = MyListwidget()
        LIST.setFixedWidth(250)                                             #limit width of list widget
        LIST.addItems([])                                                   #initiate list_widget
        LIST.setSelectionMode(QtW.QAbstractItemView.ExtendedSelection)      # ??            
        
        #left column layout
        self.left_widget = QtW.QWidget()
        self.btn_widget = QtW.QHBoxLayout()
        self.left_layout = QtW.QVBoxLayout(self)
        self.btn_widget.addWidget(self.btn_file_dial)
        self.btn_widget.addWidget(self.btn_load)
        self.left_layout.addLayout(self.btn_widget)                         #make nested layouts
        self.left_layout.addWidget(self.mpl_can)
        self.left_layout.addWidget(self.can_titel, alignment=Qt.AlignCenter) 
        self.left_widget.setLayout(self.left_layout)

        #right layout
        self.right_layout = QtW.QVBoxLayout()
        self.right_layout.addWidget(LIST)
        self.right_layout.addWidget(self.btn_copy)
        
        #total layout
        self.central_layout = QtW.QHBoxLayout()
        self.central_layout.addWidget(self.left_widget, stretch=4)
        self.central_layout.addLayout(self.right_layout)         
        
        self.setLayout(self.central_layout)                                 #creates layout

    
    

    def load_image(self):
        """
        loads the given image into the canvas, setting the canvas.
        calls LineBuilder class for interaction
        """
        
        
        self.image_data = cv2.imread(self.path)
        #self.mpl_can.ax = self.figure.add_subplot(111)
        self.mpl_can.ax.clear()                                            #clear canvas when btn is clicked
        LIST.clear()                                                                            
        self.mpl_image = self.mpl_can.ax.imshow(self.image_data) 
        self.mpl_can.ax.set_xlim(0,self.image_data[:,:,0].shape[1])
        self.mpl_can.ax.set_ylim(0,self.image_data[:,:,0].shape[0])
        #call point marker event with/on loaded image
        self.linebuilder = LineBuilder(self.mpl_image,self.mpl_can, LIST,self.path,'red')    
        self.mpl_can.ax.invert_yaxis()
        disconnect_zoom = zoom_factory(self.mpl_can.ax)
        
        self.mpl_can.can.draw()                                              #show
        



    def getfile(self):
        """
        manages the file brows dialog and returns the filepath
        """
        
        
        if self.brows_or_dir == None:
            self.brows_or_dir = 'c:\\'
        fname = QtW.QFileDialog.getOpenFileName(self, 'Open file', self.brows_or_dir,"Image files (*.jpg *.gif)")
        self.path =  fname[0]
        self.brows_or_dir = str(Path(fname[0]).parent.absolute())
        




    def CopyClipboard(self):
        """
        This function is called when the 'copy' button is clicked
        stores created list in the system clipboard
        """
        
        ClipBoard = QtW.QApplication.clipboard()
        CopyList = self.ClipBoardList()
        ClipBoard.setText("\n".join(CopyList), mode=ClipBoard.Clipboard)





    def ClipBoardList(self):
        """
        reads content from LIST widget
        copies relevant Shape number, shapesize and Ax-sizes to a new/smaller list 

        Returns:
            NewList (list): content list of relevant information that will be copied to clipboard
        """
        
        
        ListItems = [str(LIST.item(i).text()) for i in range(LIST.count())]
        NewList = []
        for item in range(len(ListItems)):
            if any(substr in ListItems[item] for substr in ["Shape", "Shapesize" ,"Ax"]):
                NewList.append(ListItems[item])
            elif ListItems[item] == "":
                NewList.append(ListItems[item])
    
        return NewList
 




#################################################################################




if __name__ == '__main__':
    app = QtW.QApplication([])
    qt_app = MyQtApp()
    qt_app.show()
    app.exec_()