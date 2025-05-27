# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.2.1-0-g80c4cb6)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

import gettext
_ = gettext.gettext

###########################################################################
## Class MainWindowBase
###########################################################################

class MainWindowBase ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"演示主窗口"), pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer1 = wx.BoxSizer( wx.VERTICAL )

        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        self.lbl_name = wx.StaticText( self, wx.ID_ANY, _(u"名字"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_name.Wrap( -1 )

        bSizer2.Add( self.lbl_name, 0, wx.ALL, 5 )

        self.txt_name = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.txt_name, 1, wx.ALL, 5 )


        bSizer1.Add( bSizer2, 0, wx.EXPAND, 5 )

        bSizer3 = wx.BoxSizer( wx.HORIZONTAL )

        self.btn_click_me = wx.Button( self, wx.ID_ANY, _(u"点我"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer3.Add( self.btn_click_me, 0, wx.ALL, 5 )


        bSizer1.Add( bSizer3, 1, wx.ALIGN_CENTER_HORIZONTAL, 5 )


        self.SetSizer( bSizer1 )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.btn_click_me.Bind( wx.EVT_BUTTON, self.open_hello_dialog )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def open_hello_dialog( self, event ):
        event.Skip()


###########################################################################
## Class dlg_hello
###########################################################################

class dlg_hello ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"欢迎"), pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer4 = wx.BoxSizer( wx.VERTICAL )

        self.lbl_name = wx.StaticText( self, wx.ID_ANY, _(u"MyLabel"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_name.Wrap( -1 )

        bSizer4.Add( self.lbl_name, 0, wx.ALL, 5 )


        self.SetSizer( bSizer4 )
        self.Layout()
        bSizer4.Fit( self )

        self.Centre( wx.BOTH )

    def __del__( self ):
        pass


