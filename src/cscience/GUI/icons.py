from wx.lib.embeddedimage import PyEmbeddedImage

catalog = {}
index = []

ART_GRAPH = 'ART_GRAPH'
ART_CALC = "ID_FOR_CALCULATOR_ICON"
ART_VIEW_ATTRIBUTES = "ID_FOR_VIEW_ATTRIBUTES_ICON"
ART_FILTER = "ID_FOR_FILTER_ICON"
ART_ANALYZE_AGE = "ID_FOR_ANALYZE_AGES_ICON"
ART_SORT_ASCENDING = "ID_FOR_SORT_ASCENDING_ICON"
ART_SORT_DESCENDING = "ID_FOR_SORT_DESCENDING_ICON"
ART_GRAPHING_OPTIONS = "ID_FOR_GRAPHING_OPTIONS_ICON"
ART_REFRESH_AI = "ID_FOR_REFRESHING_AI_CALCULATIONS"
ART_RADIO_ON = "ID_FOR_RADIOBUTTON_ON_ICON"
ART_RADIO_OFF = "ID_FOR_RADIOBUTTON_OFF_ICON"
ART_SAVE_IMAGE = "ID_FOR_SAVE_IMAGE_ICON"
ART_GRAPHED_LINES = "ID_FOR_SIMPLE_LINES_ICON"
ART_SINGLE_CURVE = "ID_FOR_SINGLE_LINE_CURVE_ICON"
ART_CONTRACT_RS = "ID_FOR_CONTRACT_RIGHT_SIDE_ICON"

index.append('GRAPH')
catalog['GRAPH'] = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0"
    "RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAJYSURBVDjLY/j//z8DJRhMmJQd"
    "+x89/W4IRQbY1x5L8590dzmy5PuIqC4gfvA+PPIyEMfhNqD06H+L9gfG9p33/jr23OMEiX30"
    "DTj8yT/oFxCf+hAYfBeIfwPxIyBWwjSg5Mh/tYZHzDr1D34aND7Y9tXOsf2Lg/O/z85uNjCF"
    "n908lT56eH985xXwzXvygwYUA4yLD/9Xcm+QlS572JWesP7XVyOL79/MLKci22Rc/6DXvPH+"
    "X8um+79t2u7/tOu4/w9ugFHxof8wha+1LP89NHT9iaxZIf/BCpWie7/Vi+/N/25kqvrN2Oz/"
    "suiO6QgDig6ADfgtJrX0p6TMb1u/Xd+5Eh9M4k16yCyQdH+HYOK9H6JJd+tgBv7U0j3wXVvv"
    "A9wAg8J9/6sNAvT/8gr++8Mn1MYQ8aCFIfzBf6bwB3+Zwx/8Ywu7H44e+j8VVX4hDMjf+/8/"
    "I6v/fya2OyghHHCn3GuRw3TvJTZnPJdYnXVbbA436Le49Aa4Afp5u///ZGAJ+c3AIg5T4DXT"
    "0stjpuULj1nmD9xmW6x1nWu2z2W+6RenBcbxIHmga6XgBujl7vw/R1TDAabZscNommOn0UeH"
    "LsNFDj2GPDBxh37DDrtJ+u8x0oFu9vb/liU6khal2jPNS3UfAem3FmU6Gej+tqjX5rBo0rln"
    "1qI9GdWArG3/jTI0/Q0z1N3UAyxdgTQ4NQpreMjCFAqpOoHZRvnqUhpROhmmxRo8cAO0M7f8"
    "187Y/F8rYxMQb/yvlbYBiNf/1wTh1HX/NUA4ZS0Ur/mvkbwajOEGUIIBf5BxjDvwFIUAAAAA"
    "SUVORK5CYII=")


import wx
import os
import sys

#TODO: For release (or once we have the icons finalized), convert this
#ArtProvider to use Img2PyArtProvider and embedded images.

class ArtProvider(wx.ArtProvider):

    iconfiles = {ART_CALC: 'calculator_black.png',
                 ART_VIEW_ATTRIBUTES: 'table_select_column.png',
                 ART_FILTER: 'table_select_row.png',
                 ART_ANALYZE_AGE: 'timeline_marker.png',
                 ART_SORT_ASCENDING: 'sort_ascending.png',
                 ART_SORT_DESCENDING: 'sort_descending.png',
                 ART_GRAPHING_OPTIONS: 'cog_edit.png',
                 ART_REFRESH_AI: 'arrow_refresh_small.png',
                 ART_RADIO_ON: 'bullet_black.png',
                 ART_RADIO_OFF: 'bullet_white.png',
                 ART_SAVE_IMAGE: 'picture_save.png',
                 ART_GRAPHED_LINES: 'chart_line_edit.png',
                 ART_SINGLE_CURVE: 'draw_wave.png',
                 ART_CONTRACT_RS: 'application_side_contract.png'
                }

    def GetBitmapFromFile(self,filepath,scale_size=None):
        try:
            img = wx.Image(filepath,type=wx.BITMAP_TYPE_PNG)

            if scale_size is not None:
                img = img.Scale(scale_size[0], scale_size[1])

            bmp = wx.BitmapFromImage(img)
        except Exception:
            print("bmp file for icon not found.")
            bmp = wx.NullBitmap
        return bmp

    def CreateBitmap(self, artid, client, size):
        path = ""
        if getattr(sys, 'frozen', False):
            # we are running in a |PyInstaller| bundle
            path = sys._MEIPASS
        else:
            path = os.path.join(os.getcwd(), os.pardir)

        path = os.path.join(path, "resources", "fatcow-hosting-icons-3000")

        if size == 32:
            path = os.path.join(path,"32x32")
        else:
            path = os.path.join(path,"16x16")

        if artid in self.iconfiles:
            return self.GetBitmapFromFile(os.path.join(path, self.iconfiles[artid]))
        else:
            return wx.NullBitmap
