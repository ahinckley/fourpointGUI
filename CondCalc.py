from __future__ import division
import wx
import wx.grid as gridlib
import os
import numpy as np
import math
from fourpointeqn import FourPointCalculation
from EditGridClass import MyGrid

class Single(wx.Frame):
    def __init__(self, parent, title,handler=None):
        self.dirname=''
        self.handler = handler

        # A "-1" in the size parameter instructs wxWidgets to use the default size.
        # In this case, we select 200px width and the default height.
        wx.Frame.__init__(self, parent, title=title, size=(650,600))

        self.initialize(handler)

        ## Items in Frame
        # First create frame
        self.left_frame = wx.BoxSizer(wx.VERTICAL)


        #Create 'select geometry' button
        geometry = wx.RadioBox(
                self, -1, "Sample Geometry", wx.DefaultPosition, wx.DefaultSize,
                ['Circle','Rectangle'], 2, wx.RA_SPECIFY_COLS)
        #Add to frame
        self.left_frame.Add(geometry, 0, wx.EXPAND)
        #Add geometry selection event
        self.Bind(wx.EVT_RADIOBOX, handler.GeomSelect, geometry)

        #upload figure
        png = wx.Image('geomFig.png', wx.BITMAP_TYPE_PNG)
        width,height = png.GetWidth(), png.GetHeight()
        png.Rescale(350,int(350*height/width)) #rescale
        GeomFig = wx.StaticBitmap(self, wx.ID_ANY, png.ConvertToBitmap())
        # Add figure to frame
        self.left_frame.Add(GeomFig, 0, wx.EXPAND)

        #Enter Geometry
        # Create new frame for the geometry inputs
        input_frame = wx.BoxSizer( wx.VERTICAL )

        input_panel_title = wx.StaticBox(self, -1, "Refer to schematic above for specified dimensions" )
        input_panel = wx.StaticBoxSizer( input_panel_title, wx.VERTICAL )
        input_grid = wx.FlexGridSizer( cols=3 )

        # Group of Dimension Inputs
        self.group1_ctrls = []
        dim0 = wx.StaticText(self, -1, " ")
        dim1 = wx.StaticText(self, -1, "s")
        dim2 = wx.StaticText(self, -1, "d")
        dim3 = wx.StaticText(self, -1, "a")
        dim4 = wx.StaticText(self, -1, "t")
        radio0 = wx.StaticText(self, -1, "inch  cm  mm")
        radio1 = wx.RadioBox(self, -1,'', wx.DefaultPosition,wx.DefaultSize,
                             ['','',''], 3,style = wx.RB_GROUP )
        radio2 = wx.RadioBox(self, -1,'', wx.DefaultPosition,wx.DefaultSize,
                             ['','',''], 3,style = wx.RB_GROUP )
        radio3 = wx.RadioBox(self, -1,'', wx.DefaultPosition,wx.DefaultSize,
                             ['','',''], 3,style = wx.RB_GROUP )
        radio4 = wx.RadioBox(self, -1,'', wx.DefaultPosition,wx.DefaultSize,
                             ['','',''], 3,style = wx.RB_GROUP )
        text0 = wx.StaticText(self, -1, "Geometry Values")
        text1 = wx.TextCtrl( self, -1, "" )
        text2 = wx.TextCtrl( self, -1, "" )
        text3 = wx.TextCtrl( self, -1, "" )
        text4 = wx.TextCtrl( self, -1, "" )
        self.group1_ctrls.append((dim0, radio0, text0))
        self.group1_ctrls.append((dim1, radio1, text1))
        self.group1_ctrls.append((dim2, radio2, text2))
        self.group1_ctrls.append((dim3, radio3, text3))
        self.group1_ctrls.append((dim4, radio4, text4))

        for dim, radio, text in self.group1_ctrls:
            input_grid.Add( dim, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
            input_grid.Add( text, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
            input_grid.Add( radio, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

        text3.Enable(False)
        text3.SetBackgroundColour((200,200,200))
        self.s,self.d,self.a,self.t = text1,text2,text3,text4
        self.Rs,self.Rd,self.Ra,self.Rt = radio1,radio2,radio3,radio4
        

        input_panel.Add( input_grid, 0, wx.ALIGN_CENTRE|wx.ALL, 5 )
        input_frame.Add( input_panel, 0, wx.ALIGN_CENTRE|wx.ALL, 5 )
        self.left_frame.Add(input_frame)


        # Create measurement button
        self.run = wx.Button(self,10,"Get Conductivity")
        # Calculate Conductivity event
        self.run.Bind(wx.EVT_BUTTON, handler.CalculateCond)
        # Add button to frame
        self.left_frame.Add(self.run, 0, wx.EXPAND)

        #Format results
        results_box = wx.BoxSizer(wx.VERTICAL)
        font = self.GetFont()
        font.SetPointSize(14)
        font.SetWeight(wx.FONTWEIGHT_BOLD)

        results_box.Add(wx.StaticLine(self, -1), 0, wx.EXPAND)
        self.AddText(results_box, self.handler.sheetresistivity, 'Sheet Resistivity (Ohm/sq):', font)
        self.AddText(results_box, self.handler.resistivity, 'Resistivity (Ohm*cm):', font)
        self.AddText(results_box, self.handler.conductivity, 'Conductivity (S/cm):', font)
        results_border = wx.BoxSizer(wx.VERTICAL)
        results_border.Add(results_box, 1, wx.EXPAND|wx.ALL, 10)
        self.left_frame.Add(results_border,0,wx.EXPAND)

        self.final_layout = wx.BoxSizer(wx.HORIZONTAL)
        self.final_layout.Add(self.left_frame, 0, wx.RIGHT)


        # Voltage and current grid
        IVgrid = gridlib.Grid(self,size=(250,-1))
        IVgrid.CreateGrid(40,3)
        columns = ['Current (A)','AV (V)','BV (V)']
        for i in range(3):
            IVgrid.SetColLabelValue(i,columns[i])
        IVgrid.SetColLabelSize(60)
        IVgrid.SetRowLabelSize(2)
        IVgrid.EnableEditing(True)
        self.IVgrid = IVgrid #MyGrid(IVgrid)
        # Modification Events
        self.Bind(gridlib.EVT_GRID_CELL_CHANGING, handler.OnCellChange)
        #Add to GUI window
        self.final_layout.Add(self.IVgrid, 0, wx.RIGHT)

        #Layout sizers
        self.SetSizer(self.final_layout)
        self.SetAutoLayout(True)
        self.Show()

    def initialize(self,handler):
        self.CreateStatusBar()  # A Statusbar in the bottom of the window

        # Setting up the menu.
        filemenu = wx.Menu()
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", " Information about this program")
        menuExit = filemenu.Append(wx.ID_EXIT, "&Exit", " Terminate the program")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")  # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # Basic Events
        self.Bind(wx.EVT_MENU, handler.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, handler.OnAbout, menuAbout)


    def AddLine(self, sizer):
        sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND)

    def AddText(self, sizer, text1, title='', font=None):
        # create some controls
        title  = wx.StaticText(self, -1, title)
        text1 = wx.StaticText(self, -1, text1)
        if font is not None:
            text1.SetFont(font)
        # put them in a sizer
        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(title)
        row.Add((15,10))
        row.Add(text1, 1, wx.EXPAND)
        # put the row in the main sizer
        sizer.Add(row, 0, wx.EXPAND|wx.ALL, 5)
        sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND)


class Application():
    
    def __init__(self,parent,title):
        self.sheetresistivity,self.resistivity,self.conductivity = '','',''
        self.GUI = Single(parent,title,handler=self)
    
    def OnAbout(self,event):
        # Create a message dialog box
        dlg = wx.MessageDialog(self.GUI,
                               "Written by Allison Hinckley, 10/11/2017. Calculations from S. Yilmaz, J. Semicond. 36(8), 2016 / F.M. Smits, Bell Sys. Tech. J. 1958",
                                "Python Program for Calculating Four Point Conductivity",
                               wx.OK)
        dlg.ShowModal() # Shows it
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self,event):
        self.GUI.Close(True)  # Close the frame.

    
    ##Program specific: 
    def GeomSelect(self, event):
        print('Selected Geometry: %d\n' % (event.GetInt()+1))
        if event.GetInt():
            self.GUI.a.Enable(True)
            self.GUI.a.SetBackgroundColour(wx.WHITE)
        else:
            self.GUI.a.SetValue('')
            self.GUI.a.SetBackgroundColour((200,200,200))
            self.GUI.a.Enable(False)

    def OnCellChange(self, evt):
        value_str = evt.GetString()
        try:
            value_float = float(value_str)
        except:
            dlg = wx.MessageDialog(self.GUI,'Enter numbers only!','WARNING',wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
            evt.Veto()
                              
    def CalculateCond(self,event):
        print('Calculation in Process')
        self.calculator = FourPointCalculation(provider=self)

        R = []
        row_empty = False
        row = 0
        while not row_empty:
            get_nums = lambda col: str(self.GUI.IVgrid.GetCellValue(row, col))
            nums_strings = map(get_nums, [0, 1, 2])
            if '' in nums_strings:
                row_empty = True
            else:
                nums = [float(_) for _ in num_strs]
                if abs(nums[0]) > 1e-7:
                    R.append(nums[0] / (nums[1] - nums[2]))
            row += 1
        self.R = R

    def GetDimensions(self):
        dimensions = []
        variables = ['s','d','a','t']
        if not self.GUI.a.Enabled:
            self.GUI.a.SetValue('0')
        values = [self.GUI.s, self.GUI.d, self.GUI.a, self.GUI.t]
        units = [self.GUI.Rs, self.GUI.Rd, self.GUI.Ra, self.GUI.Rt]
        conversion_factor = {0:2.54,1:1,2:10}
        for i in range(4):
            value = float(values[i].GetValue())
            unit = units[i].GetSelection()
            value_cm = value*conversion_factor[unit]
            dimensions.append((variables[i],value_cm))
        return dimensions

app = wx.App(False)
runner = Application(None,"Single Four Point Measurement")
app.MainLoop()

