"""
testing.py

* Copyright (c) 2006-2012, University of Colorado.
* All rights reserved.
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*     * Redistributions of source code must retain the above copyright
*       notice, this list of conditions and the following disclaimer.
*     * Redistributions in binary form must reproduce the above copyright
*       notice, this list of conditions and the following disclaimer in the
*       documentation and/or other materials provided with the distribution.
*     * Neither the name of the University of Colorado nor the
*       names of its contributors may be used to endorse or promote products
*       derived from this software without specific prior written permission.
*
* THIS SOFTWARE IS PROVIDED BY THE UNIVERSITY OF COLORADO ''AS IS'' AND ANY
* EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
* WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
* DISCLAIMED. IN NO EVENT SHALL THE UNIVERSITY OF COLORADO BE LIABLE FOR ANY
* DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
* (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
* LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
* ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
* (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
* SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


from reasoning import rule_list, samples, engine

import wx
import gui.main_window


def runTest1():
    #no process test
    return doTest({"type":"lava flow"},
                  [{"name":"A", "age":10500, "age uncertainty":200, "elevation":1000, "latitude":10},
                   {"name":"B", "age":10600, "age uncertainty":150, "elevation":500, "latitude":10},
                   {"name":"C", "age":10400, "age uncertainty":175, "elevation":750, "latitude":10},
                   {"name":"D", "age":10550, "age uncertainty":400, "elevation":800, "latitude":10}])
    
    
def runTest2():
    #outlier (last sample) test
    return doTest({"type":"moraine"},
                  [{"name":"A", "age":105000, "age uncertainty":5000, "chemistry":"A", "location":"A",
                           "boulder size":5, "in matrix":True, "elevation":5000, "latitude":50},
                   {"name":"B", "age":110000, "age uncertainty":4000, "chemistry":"A", "location":"A",
                           "boulder size":10, "in matrix":True, "elevation":4000, "latitude":50},
                   {"name":"C", "age":109000, "age uncertainty":7000, "chemistry":"A", "location":"A",
                           "boulder size":3, "in matrix":True, "elevation":3000, "latitude":50},
                   {"name":"D", "age":50000, "age uncertainty":15000, "chemistry":"B", "location":"B",
                           "boulder size":7, "in matrix":False, "elevation":2000, "latitude":51},
                   {"name":"E", "age":106000, "age uncertainty":6000, "chemistry":"A", "location":"A",
                           "boulder size":12, "in matrix":True, "elevation":2000, "latitude":50}])
    
def runTest3():
    #inheritance test
    #NOT BORKEN!
    return doTest({"type":"moraine", "flat crest":True},
                         #   "minimum age":8500, "maximum age":11000}, 
                    [{"name":"A", "age":10000, "age uncertainty":300, "chemistry":"A", "location":"A",
                           "boulder size":10, "elevation":5000, "latitude":30},
                     {"name":"B", "age":10500, "age uncertainty":500, "chemistry":"A", "location":"A",
                           "boulder size":5, "elevation":5000, "latitude":29},
                     {"name":"C", "age":13000, "age uncertainty":400, "chemistry":"A", "location":"A",
                           "boulder size":7, "elevation":5000, "latitude":32}])
    
def runTest4():
    #erosion test
    return doTest({"type":"moraine", "flat crest":True},
                   [{'name':'A', "age":95000, "age uncertainty":5000, "chemistry":"A"},
                    {'name':'B', "age":100000, "age uncertainty":6000, "chemistry":"A"},
                    {'name':'C', "age":105000, "age uncertainty":4000, "chemistry":"A"},
                    {'name':'D', "age":110000, "age uncertainty":4500, "chemistry":"A"},
                    {'name':'E', "age":115000, "age uncertainty":5500, "chemistry":"A"}])

def doTest(data, sams):
    samples.landformData = data
    samples.sampleList = [samples.CalvinSample(sample) for sample in sams]
    
    return engine.explainAges()

    
def showWindow():
    #rule_list.createRules()
    #dict = runTest1()
    dict = runTest2()
    #dict = runTest3()
    #dict = runTest4()
    
    frame = gui.main_window.CalvinFrame()
    frame.showArguments(dict)
    frame.Show()
    
if __name__ == "__main__":
    
    app = wx.PySimpleApp()
    showWindow()
    app.MainLoop()
    
    
