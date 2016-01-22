import os

import wx
import custom
from wx.lib.agw import aui
from wx.lib.agw import persist
from wx.lib.scrolledpanel import ScrolledPanel

from cscience.GUI import icons
from cscience.GUI.graph.options import PlotOptionSet

from calvin.PlotInterface import  run_with_annotations as RWA

import backend, options, plotting, events
import itertools

ADD_PLOT_ID = wx.NewId()

def get_distribution(original_point):
    def clip(points):
        top = max([i.y for i in points]) * 0.001
        return [i for i in points if i.y > top]

    dist = original_point.uncertainty.distribution
    if hasattr(dist, "x"):
        x_points = dist.x
        y_points = dist.y
        ret =  [backend.PlotPoint(x, y, None, None, None) for (x,y) in zip(x_points, y_points)]
        return clip(ret)
    else:
        return None

class PlotWindow(wx.Frame):

    def __init__(self, parent, samples, view):
        super(PlotWindow, self).__init__(parent, wx.ID_ANY, samples[0]['core'], size=(1000, 600))
        self.SetName('Plotting Window '+samples[0]['core'])

        self._mgr = aui.AuiManager(self,
                    agwFlags=aui.AUI_MGR_DEFAULT & ~aui.AUI_MGR_ALLOW_FLOATING)

        self.samples = backend.SampleCollection(samples, view)
        atts = self.samples.get_numeric_attributes()
        copts = options.PlotCanvasOptions()

        self.toolbar = Toolbar(self, atts, copts,
                            atts, self.samples.get_computation_plans())

        self._mgr.AddPane(self.toolbar, aui.AuiPaneInfo().Name('gtoolbar').
                          Layer(10).Top().DockFixed().Gripper(False).
                          CaptionVisible(False).CloseButton(False))

        # panel = wx.Panel(self)
        splitter = wx.SplitterWindow(self)
        self.splitter = splitter
        splitter.SetSashGravity(1.0)
        self.main_canvas = plotting.PlotCanvas(splitter)
        self.infopanel = InfoPanel(splitter)
        splitter.SplitVertically(self.main_canvas, self.infopanel)
        # sizer = wx.BoxSizer(wx.HORIZONTAL)
        # sizer.Add(self.main_canvas)
        # panel.SetSizerAndFit(sizer)

        self._mgr.AddPane(splitter, aui.AuiPaneInfo().Name('Main Plot').
                          Layer(9).Center().Dock().Gripper(False).
                          CaptionVisible(False).CloseButton(False).
                          Movable(False).Resizable(True))

        # self.zoom_canv_ind = plotting.PlotCanvas(self)
        # self.zoom_canv_dep = plotting.PlotCanvas(self)

        # self._mgr.AddPane(self.infopanel, aui.AuiPaneInfo().Name('ginfopanel').
        #                   Layer(10).Right().DockFixed().Gripper(False).
        #                   CaptionVisible(False).CloseButton(False).Resizable(True))

        self.Bind(events.EVT_GRAPHPTS_CHANGED, self.build_pointset_evt)
        self.Bind(events.EVT_GRAPHOPTS_CHANGED, self.update_options)
        self.Bind(events.EVT_GRAPH_PICK, self.show_zoom, self.main_canvas)
        self.Bind(events.EVT_REFRESH_AI, self.ai_refreshed)
        self.Bind(events.EVT_R2_UPDATE, self.r2_update)
        self.Bind(events.EVT_GRAPH_MOTION, self.on_motion)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        #TODO: store options here perhaps?
        # persist.PersistenceManager.Get().RegisterAndRestore(self)
        self._mgr.Update()

        self.toolbar.vars_changed() # should this be in the constructor
                                    # of toolbar? Probably...
    def on_motion(self, event):
        self.infopanel.set_cursor_x_value("%0.02f"%event.x if event.x else "")
        self.infopanel.set_cursor_y_value("%0.02f"%event.y if event.y else "")

    def r2_update(self, event):
        self.infopanel.set_y_intercept("%.02f"%(event.y_intcpt))
        self.infopanel.set_slope(      "%.02f"%(event.slope))
        self.infopanel.set_r_value(    "%.02f"%(event.r_value))
        self.infopanel.set_p_value(    "%.02f"%(event.p_value))
        self.infopanel.set_stderr(     "%.02f"%(event.std_err))
        # self.infopanel.set_attributes([
        #         ("slope", str(event.slope)),
        #         ("y-intercept", str(event.y_intcpt)),
        #         ("r-value", str(event.r_value)),
        #         ("p-value", str(event.p_value)),
        #         ("stderr", str(event.std_err))
        #     ])

    def ai_refreshed(self, event):
        '''
        fill this in with useful stuff at some point
        '''

    def on_close(self, event):
        event.Skip()
        persist.PersistenceManager.Get().SaveAndUnregister(self)

    def show_zoom(self, event):
        self.Freeze()

        self.infopanel.zoom_canv_ind.clear()
        self.infopanel.zoom_canv_dep.clear()

        if event.pointset:
            self.infopanel.set_x_varname(event.pointset.independent_var_name)
            self.infopanel.set_y_varname(event.pointset.variable_name)
        # get the distributions for both the independent
        # and dependent variables
        if event.distpoint is not None:
            self.infopanel.set_selected_x("%.02f"%event.distpoint.x)
            self.infopanel.set_selected_y("%.02f"%event.distpoint.y)

            plot_points_x = get_distribution(event.distpoint.xorig)
            plot_points_y = get_distribution(event.distpoint.yorig)

            if plot_points_x:
                opts = options.PlotOptions(fmt='-', is_graphed=True, color='#ddaaaa')
                self.infopanel.zoom_canv_ind.add_points(backend.PointSet(plot_points_x), opts)

            if plot_points_y:
                opts = options.PlotOptions(fmt='-', is_graphed=True, color='#aaaadd')
                self.infopanel.zoom_canv_dep.add_points(backend.PointSet(plot_points_y), opts)

        self.infopanel.zoom_canv_ind.update_graph()
        self.infopanel.zoom_canv_dep.update_graph()

        self._mgr.Update()
        self.Thaw()

    def collapse(self, evt=None):
        self.Freeze()

        if not self.splitter.IsSplit():
            self.splitter.SplitVertically(self.splitter.GetWindow1(), self.infopanel)
        else:
            self.splitter.Unsplit(self.splitter.GetWindow2())

        self._mgr.Update()
        self.Thaw()

    def build_pointset_evt(self, evt):

        self.build_pointset(
            evt.independent_variable,
            evt.dependent_variable_options)

    def build_pointset(self, ivar, dvars):
        assert(ivar != None)
        self.main_canvas.clear()


        for opts in dvars:
            self.main_canvas.pointsets.append((self.samples.get_pointset(ivar, opts.dependent_variable, opts.computation_plan), opts))

        self.main_canvas.update_graph()

    def update_options(self, evt=None):
        self.main_canvas.canvas_options = self.toolbar.canvas_options

    def export_graph_image(self, evt=None):
        dlg = wx.FileDialog(self, message="Export plot as ...", defaultDir=os.getcwd(),
                wildcard="Scalable Vector Graphics (*.svg)|*.svg| BMP File (*.bmp)|*.bmp| JPEG Image (*.jpg)|*.jpg| EPS File (*.eps)|*.eps| PDF File (*.pdf)|*.pdf", style=wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.main_canvas.export_to_file(path)
        dlg.Destroy()


class OptionsPane(wx.Dialog):

    def __init__(self, parent, curoptions):
        super(OptionsPane, self).__init__(parent)

        self.elements = {}
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY), wx.VERTICAL)

        for label, key in [("Show Axes Labels", 'show_axes_labels'),
                           ("Show Legend", 'legend'),
                           ("Show Grid", 'show_grid'),
                           ("Invert X Axis", 'invert_x_axis'),
                           ("Invert Y Axis",  'invert_y_axis'),
                           ("Flip Axis",  'flip_axis'),
                           ("Show Error Bars", 'show_error_bars'),
                           ("Large Font", 'large_font')]:
            cb = wx.CheckBox(self, wx.ID_ANY, label=label)
            cb.SetValue(getattr(curoptions, key))
            self.elements[key] = cb
            sizer.Add(cb, wx.EXPAND)

        okbtn = wx.Button(self, wx.ID_OK)
        okbtn.SetDefault()
        cancelbtn = wx.Button(self, wx.ID_CANCEL)

        bsizer = wx.StdDialogButtonSizer()
        bsizer.Add(okbtn, flag=wx.ALL, border=5)
        bsizer.Add(cancelbtn, flag=wx.ALL, border=5)
        bsizer.Realize()
        sizer.Add(bsizer, border=5)

        self.SetSizerAndFit(sizer)

    def get_canvas_options(self):
        return options.PlotCanvasOptions(**dict([(key, cb.IsChecked())
                    for key, cb in self.elements.items()]))


class ShapeCombo(wx.combo.OwnerDrawnComboBox):
    """
    An awesome combobox for matplotlib shapey goodness
    """
    # current failings: all my shapes are pinned to a size of ~10x10, which is
    # fine but highly important to know
    def draw_sq(dc, r):  # s
        dc.DrawRectangle(r.x, r.y, 10, 10)

    def draw_cir(dc, r):  # o
        dc.DrawCircle(r.x+5, r.y+5, 5)

    def draw_tri(dc, r):  # ^
        dc.DrawPolygon([(r.x, r.y+10), (r.x+5, r.y), (r.x+10, r.y+10)])

    def draw_dia(dc, r):  # d
        dc.DrawPolygon([(r.x+2, r.y+5), (r.x+5, r.y),
                        (r.x+8, r.y+5), (r.x+5, r.y+10)])

    def draw_sta(dc, r):  # *
        dc.DrawPolygon([(r.x+2, r.y+10), (r.x+3, r.y+7),
                        (r.x, r.y+4), (r.x+4, r.y+4),
                        (r.x+5, r.y), (r.x+6, r.y+4),
                        (r.x+10, r.y+4), (r.x+7, r.y+7),
                        (r.x+8, r.y+10), (r.x+5, r.y+8)])

    SHAPES = {'s': draw_sq, 'o': draw_cir,
              '^': draw_tri, 'd': draw_dia,
              '*': draw_sta, '': lambda *args: 0}

    def __init__(self, *args, **kwargs):
        super(ShapeCombo, self).__init__(*args, choices=('s', 'o', '^', 'd', '*', ''),
                                         style=wx.CB_READONLY, size=(48,-1), **kwargs)

    def OnDrawItem(self, dc, rect, item, flags):
        """
        Draws each item in the drop-down
        """
        if item == wx.NOT_FOUND:
            # painting the control, but there is no valid item selected yet
            return
        r = wx.Rect(*rect)  # make a copy
        r.Deflate(3, 5)

        shape = self.GetString(item)
        dc.SetBrush(wx.Brush((0, 0, 0)))
        dc.SetPen(wx.Pen((0, 0, 0)))  # even if we're highlighted, keep the pen black
        ShapeCombo.SHAPES[shape](dc, r)

    # Overridden from OwnerDrawnComboBox, should return the height
    # needed to display an item in the popup, or -1 for default
    def OnMeasureItem(self, item):
        return 24

    # Overridden from OwnerDrawnComboBox.  Callback for item width, or
    # -1 for default/undetermined
    def OnMeasureItemWidth(self, item):
        return 24


class StylePane(wx.Dialog):
    class CustomColorButton(wx.Button):
        def __init__(self, parent):
            super(StylePane.CustomColorButton, self).__init__(parent, wx.ID_ANY)
            # self.panel = wx.Panel(self, wx.ID_ANY, style=wx.SUNKEN_BORDER)
            # self.Add(pad_window(self.panel, 10))
            self.color_data = wx.ColourData()
            self.SetBackgroundColour(self.color_data.GetColour())

        def GetColor(self):
            return self.GetBackgroundColour()

        def SetColor(self, color):
            self.color_data.SetColour(color)
            self.SetBackgroundColour(color)

        def ShowDialog(self):
            dialog = wx.ColourDialog(self, self.color_data)
            dialog.ShowModal()
            self.color_data = dialog.GetColourData()
            self.SetColor(self.color_data.GetColour())


    class PaneRow(wx.Panel):
        def __init__(self, parent, option, depvars, selected_depvar, enabled=True, should_wrap=False):
            assert option.__class__ == options.PlotOptions, "option has type: %s" % option.__class__
            assert depvars.__class__ == list


            self.should_wrap = should_wrap

            # Option is the option which this PaneRow will
            # reflect.
            #
            # depvars is a list of all possible dependent variables
            # for the combobox.
            #
            # selected_depvar is the string of the selected depvar

            super(StylePane.PaneRow, self).__init__(parent, wx.ID_ANY)

            self.checkbox = wx.CheckBox(self, wx.ID_ANY, "")
            self.checkbox.SetValue(enabled)

            self.dependent_variables = wx.Choice(self, choices=depvars)
            self.dependent_variables.SetStringSelection(selected_depvar)

            self.colorpicker = wx.ColourPickerCtrl(self, wx.ID_ANY)
            self.colorpicker.SetColour(option.color)

            self.stylepicker = ShapeCombo(self)
            self.stylepicker.SetStringSelection(option.fmt)

            self.interpchoice = wx.Choice(self, choices=option.interpolations.keys())
            self.interpchoice.SetStringSelection(option.interpolation_strategy)


            self.chooseplan = wx.Choice(self, choices=option.computation_plans)
            self.chooseplan.SetStringSelection(option.computation_plan)
            self.popup = self.mk_transient_window()


            sizer = wx.BoxSizer(wx.VERTICAL)
            # self.planpopup.SetSizerAndFit(sizer)

            parent.Bind(wx.EVT_BUTTON, self.popup_cplan, self.chooseplan)
            my_sizer = wx.BoxSizer(wx.HORIZONTAL)
            my_sizer.AddSpacer(10);
            my_sizer.Add(self.mk_wrap("", self.checkbox))
            my_sizer.AddSpacer(5);
            my_sizer.Add(self.mk_wrap("Variable", self.dependent_variables))
            my_sizer.AddSpacer(5);
            my_sizer.Add(self.mk_wrap("Color", self.colorpicker))
            my_sizer.AddSpacer(5);
            my_sizer.Add(self.mk_wrap("Style", self.stylepicker))
            my_sizer.AddSpacer(5);
            my_sizer.Add(self.mk_wrap("Interpolation", self.interpchoice))
            my_sizer.AddSpacer(5);
            my_sizer.Add(self.mk_wrap("Computation Plan", self.chooseplan))
            my_sizer.AddSpacer(5);

            del_bmp = wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_TOOLBAR, (16, 16))
            remove = wx.BitmapButton(self, self.GetId(), del_bmp)
            my_sizer.Add(self.mk_wrap("", remove))
            my_sizer.AddSpacer(5);
            btn = wx.Button(self, wx.ID_ANY, "...", style=wx.BU_EXACTFIT)
            self.extra_button = btn
            my_sizer.Add(self.mk_wrap("", btn))
            my_sizer.AddSpacer(10);

            self.Bind(wx.EVT_BUTTON, self.popup_window, btn)

            self.SetSizerAndFit(my_sizer)

        def popup_window(self, _):
            pos = self.extra_button.ClientToScreen((0, 0))
            sz = self.extra_button.GetSize()
            self.popup.Position(pos, (0, sz[1]))
            self.popup.Popup()

        def on_same_point_color(self, _=None):
            if self.line_color_checkbox.GetValue():
                self.line_colorpicker.Disable()
                self.line_colorpicker.SetColor(self.colorpicker.GetColour())
            else:
                self.line_colorpicker.Enable()

        def on_line_color_picker(self, _=None):
            self.popup.Dismiss()
            self.line_colorpicker.ShowModal(self)


        def mk_transient_window(self):
            extras = wx.PopupTransientWindow(self, wx.ID_ANY)
            extras.MakeModal(False)
            panel = wx.Panel(extras, wx.ID_ANY, style=wx.SIMPLE_BORDER)

            self.line_colorpicker = custom.ColorButton(panel)
            self.line_colorpicker.SetColor((0,0,0))
            self.line_color_checkbox = wx.CheckBox(panel, wx.ID_ANY, "Same as point color")
            self.line_color_checkbox.SetValue(True)
            self.on_same_point_color()

            self.Bind(wx.EVT_CHECKBOX, self.on_same_point_color, self.line_color_checkbox)
            self.Bind(wx.EVT_BUTTON, self.on_line_color_picker, self.line_colorpicker)

            sizer = wx.GridBagSizer(5, 5)
            self.point_size = wx.SpinCtrl(panel, wx.ID_ANY, style=wx.SP_ARROW_KEYS, min=1, max=100)
            self.point_size.SetValue(6)
            self.line_width = wx.SpinCtrl(panel, wx.ID_ANY, style=wx.SP_ARROW_KEYS, min=1, max=100)
            self.line_width.SetValue(4)

            simple_add_gbsizer(sizer, simple_text(panel, "Point Size"), (0, 0))
            simple_add_gbsizer(sizer, self.point_size, (0, 1))
            simple_add_gbsizer(sizer, simple_text(panel, "Line Width"), (1, 0))
            simple_add_gbsizer(sizer, self.line_width, (1, 1))

            simple_add_gbsizer(sizer, simple_text(panel, "Line Color"), (2, 0))
            simple_add_gbsizer(sizer, simple_couple(self.line_colorpicker, self.line_color_checkbox, 5), (2, 1))

            panel.SetSizer(pad_window(sizer, 5))

            extras.SetSizerAndFit(simple_wrap(panel))

            return extras

        def mk_wrap(self, name, widget):
            if self.should_wrap:
                ret_sizer = wx.BoxSizer(wx.VERTICAL)
                ret_sizer.Add(wx.StaticText(self, wx.ID_ANY, name))
                ret_sizer.Add(widget, wx.RIGHT)
                return ret_sizer
            else:
                return widget

        def popup_cplan(self, event):
            pos = self.chooseplan.ClientToScreen((0, 0))
            sz = self.chooseplan.GetSize()
            self.planpopup.Position(pos, (0, sz[1]))
            self.planpopup.Popup()

        def get_option(self):
            return options.PlotOptions(
                        is_graphed=self.checkbox.GetValue(),
                        color=self.colorpicker.GetColour(),
                        dependent_variable=self.dependent_variables.GetStringSelection(),
                        #GetStringSelection seems to be fussy; this seems to work in all cases.
                        fmt=self.stylepicker.GetString(self.stylepicker.GetSelection()),
                        interpolation_strategy=self.interpchoice.GetStringSelection(),
                        computation_plan=self.chooseplan.GetStringSelection(),
                        point_size=self.point_size.GetValue(),
                        line_width=self.line_width.GetValue(),
                        line_color=self.line_colorpicker.GetColor() if not self.line_color_checkbox.GetValue() else self.colorpicker.GetColour()
                        )

    class InternalPanel(ScrolledPanel):
        def __init__(self, parent, dependent_variables):
            assert dependent_variables.__class__ == list
            # dependent variables is a list of strings

            self.dependent_variables = dependent_variables
            self.panel_set = set()

            super(StylePane.InternalPanel, self).__init__(parent, wx.ID_ANY, style=wx.SIMPLE_BORDER, size=(-1, 300))
            self.sizer = wx.BoxSizer(wx.VERTICAL)
            self.SetupScrolling(scroll_x = False)

            # The panel with the row headers on it
            panel = wx.Panel(self)
            panel_sizer = wx.GridBagSizer()

            panel.SetSizerAndFit(panel_sizer)
            self.sizer.Add(panel)

            new_bmp = wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR, (16, 16))

            sizer2 = wx.BoxSizer(wx.VERTICAL)
            self.addbtn = wx.Panel(self)
            addbtn_sizer = wx.BoxSizer(wx.HORIZONTAL)
            addbtn_sizer.AddSpacer(10)
            addbtn_sizer.Add(wx.BitmapButton(self.addbtn, ADD_PLOT_ID, new_bmp))
            self.addbtn.SetSizerAndFit(addbtn_sizer)
            sizer2.Add(self.sizer)
            sizer2.Add(self.addbtn)

            self.SetSizer(sizer2)


        def get_optset(self):
            return [i.get_option() for i in self.panel_set]

        def remove(self, panel):
            def handler(_):
                self.sizer.Remove(panel)
                self.panel_set.remove(panel)
                panel.Destroy()
                self.Update()
                self.Layout()

            return handler

        def add_panel(self, name, option, enabled=True):
            style_panel = StylePane.PaneRow(self, option, self.dependent_variables, name, enabled, len(self.panel_set) == 0)
            self.Freeze()

            self.panel_set.add(style_panel)
            self.sizer.Add(style_panel, flag=wx.EXPAND)
            self.Bind(wx.EVT_BUTTON, self.remove(style_panel), id=style_panel.GetId())
            (w, _) = self.sizer.GetSize()
            self.SetSize((w, 300))
            self.Update()
            self.Layout()
            self.Thaw()

    def __init__(self, parent, depvars, computation_plans):
        assert depvars.__class__ == list

        # depvars :: [string]
        # current_options :: [PlotOptions]
        #
        # Current options is used for the initial population
        # of the options.
        #
        # depvars is used as the total possible dependent
        # variables and their associated computation plans.
        super(StylePane, self).__init__(parent, wx.ID_ANY)

        sizer = wx.GridBagSizer(2, 2)
        self.rotating = 0

        self.possible_variables = depvars[:]
        self.computation_plans = computation_plans
        self.optset = PlotOptionSet.from_vars(
                    self.possible_variables,
                    self.computation_plans).values()


        def hpad(widget):
            ret_sizer = wx.BoxSizer(wx.HORIZONTAL)
            ret_sizer.AddSpacer(10)
            ret_sizer.Add(widget)
            ret_sizer.AddSpacer(10)
            return ret_sizer
        def vpad(widget):
            ret_sizer = wx.BoxSizer(wx.VERTICAL)
            ret_sizer.AddSpacer(10)
            ret_sizer.Add(widget)
            ret_sizer.AddSpacer(10)
            return ret_sizer

        self.internal_panel = StylePane.InternalPanel(self, depvars)
        sizer.Add(vpad(wx.StaticText(self, wx.ID_ANY, "Possible Plots")), (0, 0), (1, 4), flag=wx.ALIGN_CENTER_HORIZONTAL)
        sizer.Add(hpad(self.internal_panel), (1, 0), (1, 4), flag=wx.EXPAND)

        self.Bind(wx.EVT_BUTTON, self.on_add, id=ADD_PLOT_ID)

        okbtn = wx.Button(self, wx.ID_OK)
        okbtn.SetDefault()
        cancelbtn = wx.Button(self, wx.ID_CANCEL)

        bsizer = wx.StdDialogButtonSizer()
        bsizer.AddButton(okbtn)
        bsizer.AddButton(cancelbtn)
        bsizer.Realize()

        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(1)
        sizer.Add(vpad(bsizer), (3, 0), (1, 4))

        self.SetSizerAndFit(sizer)
        self.setup_init_view()

    def setup_init_view(self):
        self.Freeze()
        for opts in self.optset:
            self.internal_panel.add_panel(opts.dependent_variable, opts, opts.dependent_variable == "Best Age")
        self.Fit()
        self.Update()
        self.Layout()
        self.Thaw()


    def on_add(self, _):
        opts = self.optset[self.rotating % len(self.optset)]
        self.rotating += 1
        self.internal_panel.add_panel(opts.dependent_variable, opts)
        self.Update()
        self.Layout()

    def get_option_set(self):
        # return a list
        ret = self.internal_panel.get_optset()
        return ret

def pad_window(win, amt):
    hsizer = wx.BoxSizer(wx.HORIZONTAL)
    vsizer = wx.BoxSizer(wx.VERTICAL)
    hsizer.AddSpacer(amt)
    vsizer.AddSpacer(amt)
    vsizer.Add(win, 1, wx.EXPAND)
    vsizer.AddSpacer(amt)
    hsizer.Add(vsizer, 1, wx.EXPAND)
    hsizer.AddSpacer(amt)
    return hsizer

def simple_wrap(win):
    hsizer = wx.BoxSizer(wx.HORIZONTAL)
    hsizer.Add(win, 1, wx.EXPAND)
    return hsizer

def simple_add_gbsizer(grid, win, pos, span=(1, 1)):
    grid.Add(win, pos, span, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL)

def simple_couple(win1, win2, pad=0):
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    sizer.Add(win1)
    if pad:
        sizer.AddSpacer(pad)
    sizer.Add(win2)
    return sizer

def simple_text(parent, text):
    return wx.StaticText(parent, wx.ID_ANY, text)

class InfoPanel(ScrolledPanel):
    ''' A pane that contains information about
        stuff in the plot. Defined originally to show information
        about the linear regression line '''

    def __init__(self, parent):
        super(InfoPanel, self).__init__(parent, wx.ID_ANY, size=(-1, 50))
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        panel = wx.Panel(self, wx.ID_ANY, style=wx.RAISED_BORDER)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.make_linreg_box(panel), 1, wx.EXPAND)
        hsizer.AddSpacer(10, 1, wx.EXPAND)
        hsizer.Add(self.make_cursor_box(panel))

        panel.SetSizer(pad_window(hsizer, 5))

        self.sizer.Add(panel)
        self.sizer.AddSpacer(20)
        self.sizer.Add(self.make_distributions(),1,wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetupScrolling(scroll_x=False)

    def set_x_varname(self, str):
        self.selected_x_lab.SetLabel(str)
        self.zoom_canv_ind.delegate.figure.suptitle("Selected %s Distribution" % str)
        self.Layout()

    def set_y_varname(self, str):
        self.selected_y_lab.SetLabel(str)
        self.zoom_canv_dep.delegate.figure.suptitle("Selected %s Distribution" % str)
        self.Layout()

    def make_distributions(self):
        window = wx.SplitterWindow(self)
        window.SetSashGravity(0.5)
        self.zoom_canv_dep = plotting.PlotCanvas(window, (1,1))
        self.zoom_canv_ind = plotting.PlotCanvas(window, (1,1))
        window.SplitHorizontally(self.zoom_canv_dep, self.zoom_canv_ind)
        return window


    def make_cursor_box(self, parent):
        self.cursor_y = wx.TextCtrl(parent, wx.ID_ANY, "")
        self.cursor_y.SetEditable(False)
        self.cursor_x = wx.TextCtrl(parent, wx.ID_ANY, "")
        self.cursor_x.SetEditable(False)
        self.selected_y = wx.TextCtrl(parent, wx.ID_ANY, "")
        self.selected_y.SetEditable(False)
        self.selected_x = wx.TextCtrl(parent, wx.ID_ANY, "")
        self.selected_x.SetEditable(False)
        self.selected_y_lab = wx.StaticText(parent, wx.ID_ANY, "Selected Y")
        self.selected_x_lab = wx.StaticText(parent, wx.ID_ANY, "Selected X")

        box1 = wx.StaticBoxSizer(wx.StaticBox(parent, wx.ID_ANY, "Cursor"), wx.HORIZONTAL)
        grid = wx.GridSizer(2, 2)
        grid.Add(wx.StaticText(parent, wx.ID_ANY, "Cursor X"), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.cursor_x)
        grid.Add(wx.StaticText(parent, wx.ID_ANY, "Cursor Y"), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.cursor_y)
        box1.Add(pad_window(grid, 5))

        box2 = wx.StaticBoxSizer(wx.StaticBox(parent, wx.ID_ANY, "Selection"), wx.HORIZONTAL)
        sizer = wx.GridBagSizer(0, 10)
        sizer.Add(self.selected_y_lab, (0, 0), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.selected_x_lab, (1, 0), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(self.selected_y, (0, 1))
        sizer.Add(self.selected_x, (1, 1))

        sizer.AddGrowableRow(0)
        sizer.AddGrowableCol(0)
        # sizer = wx.BoxSizer(wx.VERTICAL)
        # sizer.Add(self.selected_y_lab)
        # sizer.Add(self.selected_y, 1, wx.EXPAND)
        # sizer.AddSpacer(10)
        # sizer.Add(self.selected_x_lab)
        # sizer.Add(self.selected_x, 1, wx.EXPAND)
        box2.Add(pad_window(sizer, 5))

        gsizer = wx.BoxSizer(wx.VERTICAL)
        gsizer.Add(box1)
        gsizer.AddSpacer(10)
        gsizer.Add(box2)

        return gsizer

    def make_linreg_box(self, parent):
        box = wx.StaticBox(parent, wx.ID_ANY, "Linear Regression Stats")
        panel = wx.Panel(box, wx.ID_ANY)
        self.y_intercept = wx.TextCtrl(panel, wx.ID_ANY, "")
        self.y_intercept.SetEditable(False)
        self.slope = wx.TextCtrl(panel, wx.ID_ANY, "")
        self.slope.SetEditable(False)
        self.r_value = wx.TextCtrl(panel, wx.ID_ANY, "")
        self.r_value.SetEditable(False)
        self.p_value = wx.TextCtrl(panel, wx.ID_ANY, "")
        self.p_value.SetEditable(False)
        self.stderr = wx.TextCtrl(panel, wx.ID_ANY, "")
        self.stderr.SetEditable(False)

        grid = wx.GridBagSizer(0, 5)
        grid.Add(wx.StaticText(panel, wx.ID_ANY, "Y-Intercept"), (0, 0))
        grid.Add(self.y_intercept, (0, 1))
        grid.Add(wx.StaticText(panel, wx.ID_ANY, "Slope"), (1, 0))
        grid.Add(self.slope, (1, 1))
        grid.Add(wx.StaticText(panel, wx.ID_ANY, "R-Value"), (2, 0))
        grid.Add(self.r_value, (2, 1))
        grid.Add(wx.StaticText(panel, wx.ID_ANY, "P-Value"), (3, 0))
        grid.Add(self.p_value, (3, 1))
        grid.Add(wx.StaticText(panel, wx.ID_ANY, "Std-Err"), (4, 0))
        grid.Add(self.stderr, (4, 1))

        panel.SetSizer(pad_window(grid, 10))
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND)
        sizer.AddSpacer(10)
        box.SetSizer(sizer)
        return box

    def set_cursor_x_value(self, cursorx):
        self.cursor_x.SetValue(cursorx)

    def set_cursor_y_value(self, cursory):
        self.cursor_y.SetValue(cursory)

    def set_selected_x(self, selx):
        self.selected_x.SetValue(selx)

    def set_selected_y(self, sely):
        self.selected_y.SetValue(sely)

    def set_r_value(self, value):
        self.r_value.SetValue(value)

    def set_p_value(self, value):
        self.p_value.SetValue(value)

    def set_stderr(self, value):
        self.stderr.SetValue(value)

    def set_y_intercept(self, value):
        self.y_intercept.SetValue(value)

    def set_slope(self, value):
        self.slope.SetValue(value)

    def set_attributes(self, tuple_list):
        "dict_of_info: list (string, string)"

        self.sizer.Clear(True)
        row = 0
        for (key, value) in tuple_list:
            label = wx.StaticText(self, wx.ID_ANY, "%s=%s" % (key, value))
            self.sizer.Add(label, (row, 0), (1, 1), wx.EXPAND)
            row += 1

        self.Layout()
        self.Fit()
        self.Update()



# class specific to a toolbar in the plot window
class Toolbar(aui.AuiToolBar):

    def __init__(self, parent, indattrs, baseopts, atts, computation_plans):
        super(Toolbar, self).__init__(parent, wx.ID_ANY, agwStyle=aui.AUI_TB_HORZ_TEXT)

        # TODO: it ought to be possible to have the aui toolbar stuff manage
        # this guy more automagically

        self.computation_plans = computation_plans
        depvar_id = wx.NewId()
        self.AddSimpleTool(depvar_id, 'Plot...',
            wx.ArtProvider.GetBitmap(icons.ART_GRAPHED_LINES, wx.ART_TOOLBAR, (16, 16)))
        self.AddLabel(wx.ID_ANY, 'vs', 13)
        self.invar_choice = wx.Choice(self, wx.ID_ANY, choices=indattrs)
        self.invar_choice.SetStringSelection('depth')
        self.AddControl(self.invar_choice)

        self.AddSeparator()
        export_id = wx.NewId()
        self.AddSimpleTool(export_id, 'Export...',
            wx.ArtProvider.GetBitmap(icons.ART_SAVE_IMAGE, wx.ART_TOOLBAR, (16, 16)))

        self.AddSeparator()
        options_id = wx.NewId()
        self.AddSimpleTool(options_id, 'Options',
            wx.ArtProvider.GetBitmap(icons.ART_GRAPHING_OPTIONS, wx.ART_TOOLBAR, (16, 16)))

        self.AddSeparator()
        ai_id = wx.NewId()
        self.AddSimpleTool(ai_id, 'Refresh AI',
            wx.ArtProvider.GetBitmap(icons.ART_REFRESH_AI, wx.ART_TOOLBAR, (16, 16)))

        self.AddStretchSpacer()
        self.contract_id = wx.NewId()
        self.AddTool(self.contract_id, '',
            wx.ArtProvider.GetBitmap(icons.ART_CONTRACT_RS, wx.ART_TOOLBAR, (16, 16)),
            wx.NullBitmap, kind=aui.ITEM_NORMAL)

        self.canvas_options = baseopts
        self.depvar_choices = atts
        self.current_depvar_choices = []

        self.Bind(wx.EVT_TOOL, self.refresh_ai, id=ai_id)
        self.Bind(wx.EVT_TOOL, self.show_options, id=options_id)
        self.Bind(wx.EVT_TOOL, self.show_dep_styles, id=depvar_id)
        self.Bind(wx.EVT_CHOICE, self.vars_changed_evt, self.invar_choice)
        self.Bind(wx.EVT_WINDOW_MODAL_DIALOG_CLOSED, self.dialog_done)

        # these are handled by parent...
        self.Bind(wx.EVT_TOOL, self.Parent.export_graph_image, id=export_id)
        self.Bind(wx.EVT_TOOL, self.Parent.collapse, id=self.contract_id)

        self.style_pane = None
        self.Realize()

    def vars_changed_evt(self, evt=None):
        self.vars_changed()

    def vars_changed(self):
        nevt = events.PointsChangedEvent(self.GetId())
        nevt.independent_variable = self.independent_variable
        nevt.dependent_variable_options = self.current_depvar_choices
        wx.PostEvent(self, nevt)

    def show_dep_styles(self, evt=None):
        if not self.style_pane:
            self.style_pane = StylePane(self, self.depvar_choices, self.computation_plans)
        self.style_pane.ShowWindowModal()

    def show_options(self, evt=None):
        OptionsPane(self, self.canvas_options).ShowWindowModal()

    def refresh_ai(self, evt=None):
        plot_hndl = wx.FindWindowByName('Plotting Window')

        RWA(plot_hndl.main_canvas.annotations)

    def dialog_done(self, event):
        dlg = event.GetDialog()
        btn = event.GetReturnCode()
        if btn == wx.ID_OK:
            if hasattr(dlg, 'get_canvas_options'):
                self.canvas_options = dlg.get_canvas_options()
                wx.PostEvent(self, events.OptionsChangedEvent(self.GetId()))
                dlg.Destroy()
            if hasattr(dlg, 'get_option_set'):
                self.current_depvar_choices = dlg.get_option_set()
                self.vars_changed()

    @property
    def independent_variable(self):
        return self.invar_choice.GetStringSelection()
