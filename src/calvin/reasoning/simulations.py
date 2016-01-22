"""
simulations.py

* Copyright (c) 2006-2009, University of Colorado.
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

"""
Simulations are functions that can be run on the right hand side of a rule.
These rules are defined in rule_list.  The Simulation class is different
and contained in rules.py

If you want to add a simulation rule, it must be added in rule_list.py and it
looks like this vvv  (<> signify user defined variables)

rules.makeRule(Conclusion("<conclusion name>",
               [rules.Simulation('<simulation function name>', [<list of args>]]
               Validity.<validityType>)

A simulation function should always be defined as a function that returns
a single SimResult object.
"""

import confidence
#import samples
import engine
import conclusions
import calculations
import observations
import csv
import os

import math
import scipy
from scipy import stats

#TODO: fiddle with these so they suck fewer balls

class SimResult(object):
    """
    Represents the result of the simulation. Eventually this will contain
    not only confidence and some sort of value stuff, but also things like
    how to display the simulation on the pretty user interface

    conf - A confidence object
    simName - The name of the simulation
    shortDesc - A description of the simulation
    guiDesc - A description of the sim for the gui
    """
    def __init__(self, conf, simName, shortDesc, guiDesc):
        self.confidence = conf
        self.sim_name = simName
        self.short_desc = shortDesc
        self.params = []
        self.gui_item = guiDesc


# This is disgusting. Let's see if we can do a bit better.
def __getConfidence(tvals, value, quality):
    """
    Returns a truth value from a range of truth values
    tvals should be a tuple containing the 5 dividing values between
    each of the truth value ranges, from most false to most true dividers
    """

    if scipy.isnan(value):
        match = confidence.Applic.cf
    elif value < tvals[0]:
        match = confidence.Applic.cf
    elif value < tvals[1]:
        match = confidence.Applic.ff
    elif value < tvals[2]:
        match = confidence.Applic.df
    elif value < tvals[3]:
        match = confidence.Applic.dt
    elif value < tvals[4]:
        match = confidence.Applic.ft
    else:
        match = confidence.Applic.ct

    return confidence.Confidence(match, quality)

def __getQuality(sig):
    """
    Converts a measure of statistical significance into a measure of simulation
    quality. Significance is assumed to be from 0-1, with larger values
    indicating less significance.

    ranges (for now) are:
    absolute 0-.01
    good .01-.05
    okay .05-.1
    poor .1+
    """

    if scipy.isnan(sig):
        return confidence.Validity.plaus
    elif sig > .1:
        return confidence.Validity.plaus
    elif sig > .05:
        return confidence.Validity.prob
    elif sig > .01:
        return confidence.Validity.sound
    else:
        return confidence.Validity.accept

