# File: graph.py  Mr Blee's prefs grapher
# Author: Brent Reeves
# Copyright: (c) 2018 Brent Reeves
# Date: Spring 2018
# Input: team member preference list:  Name,int,int,int,int...  1-based preferences in order
# Output: dot graph
# How: just loop through each prefs list, generating arcs
# Run: python graph.py -h
#      e.g.: python graph.py -v 0 < prefs.txt
#
import sys
import random
import argparse
import time
import datetime
import csv

class Arcs:
    def __init__(self, loglevel):
        self.prefs = []
        self.folks = []
        self.loglevel = loglevel
        self.keepit = []
        self.arcs = []
        self.teamcount = 0

    def log (self, level, msg):
        if level < self.loglevel:
            print(msg)

    def readStdIn(self):
        maxprefs = 0
        f = sys.stdin.readlines()
        clean = [( x.replace('\n','')) for x in f ]
        lines = 0
        for line in clean:
            lines+= 1
            row = line.split(",")
            if len(row) > 0:
                self.log(2, "row: %s" % str(row))
                redo=[]
                redo.append(row[0].replace(' ','_'))
                if len(row) - 1 > maxprefs:
                    maxprefs = len(row)
                for i in range(1,len(row)):
                    if row[i].strip() == '':
                        redo.append(0)
                    else:
                        redo.append( int( row[i] ))
                self.prefs.append( redo )

    def printHeader(self):
        print("digraph G {")

    def printEnd(self):
        print("\n}")
        
    def printArcs(self):
        self.arcs = []
        for s in self.prefs:
            for p in s[1:]:
                if (p > 0):
                    print( "%s %s %s;" % (s[0], ' -> ', self.prefs[p-1][0]))

        # for i in range(0, len(self.prefs)):
        #     for j in self.folks:
        #         self.arcs.append("%s %s %s" % (self.folks[i][0], ' -> ', self.folks[i][j] ))
        # self.log(2, "we have %d arcs" % len(self.arcs))

    def printGraph(self):
        self.printHeader()
        self.printArcs()
        self.printEnd()

    def reportArcs(self):
        # for a in self.arcs:
        #     print ( str( a ) )
        # self.arcs = []
        for s in self.prefs:
            for p in s[1:]:
                print( "s[0] %s  p %d  prefs[p-1]  %s    [p-1][0]  %s" % (s[0], p, self.prefs[p-1], self.prefs[p-1][0] ))
                # print( "%s %s %s;" % (s[0], ' -> ', self.prefs[p-1][0]))


            
if __name__ == '__main__':
    in_loglevel = 0

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="log level, default is 0.")
    
    args = parser.parse_args()
    if args.verbose:
        in_loglevel = int(args.verbose)

    a = Arcs( in_loglevel )
    a.readStdIn()
    a.printGraph()

