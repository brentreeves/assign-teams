# File: buckets-no-zeros.py  Mr Blee's Fabulous Olde Team Picker
# Author: Brent Reeves
# Copyright: (c) 2018 Brent Reeves
# Date: Spring 2018
# Input: team member preference list:  Name,int,int,int,int...  1-based preferences in order
# Output: optimized teams
# How: zillions of random swaps, while keeping number-of-zeros even-ish
# Run: python buckets.py -h
#      e.g.: python buckets.py -v 0 -t 4 -g 50000 -l 10 < prefs.txt
# python buckets.py -t 4 --calc "5, 4, 28, 31,  17, 29, 14, 6,  2, 26, 27, 8,  15, 20, 16, 32,  13, 7, 18, 12,  1, 11, 22, 30,  23, 19, 24, 21,  9, 10, 3, 25"  < prefs2.txt
#
import sys
import random
import argparse
import time
import datetime
import csv

class Buckets:
    def __init__(self, size, loops, generations, delta, overide, breadcrumbs, loglevel, planb, seed):
        self.teamsize = size
        self.prefs = []
        self.folks = []
        self.seed = seed
        self.rank = []
        self.loops = loops
        self.generations = generations
        self.delta = delta
        self.overidePercent = overide
        self.breadcrumbs = breadcrumbs
        self.loglevel = loglevel
        self.planb = planb
        self.max_score = 0
        self.keepit = []
        self.teamcount = 1
        self.countOverides = 0
        self.super_score = 0
        self.super_folks = []
        self.nixedExchanges = 0
        self.exchanges = 0


    def log (self, level, msg):
        if level < self.loglevel:
            print(msg)


    def readStdIn(self):
        maxprefs = 6
        f = sys.stdin.readlines()
        clean = [( x.replace('\n','')) for x in f ]
        for line in clean:
            row = line.split(",")
            if len(row) > 0:
                self.log(2, "row: %s" % str(row))
                redo=[]
                redo.append(row[0])
                if len(row) - 1 > maxprefs:
                    maxprefs = len(row)
                for i in range(1,len(row)):
                    if row[i].strip() =='':
                        redo.append(0)
                    else:
                        redo.append( int( row[i] ))
                self.prefs.append( redo )
        self.maybeSizeToFit()
        self.setupRank(maxprefs)
        self.setupFolks()


    def setupRank(self, max):
        # after read_prefs
        self.rank = [(max - i) for i in range(0,max)]
        self.log(2, "setupRank %d ranks: %s" % (max, str(self.rank)))


    def setupFolks(self):
        self.log(2,"setupFolks")
        self.folks = []
        for i in range(0, len(self.prefs)):
            self.folks.append(i+1)
        self.log(2, "setupFolks.len: %d  now: %s" % (len(self.folks), str(self.folks)))

    def maybeSizeToFit(self):
        self.log(2,"maybeSizeToFit")
        n = len(self.prefs)
        m = n % self.teamsize
        self.teamCount = n // self.teamsize
        if m != 0:
            newsize = (self.teamCount + 1) * self.teamsize
            for i in range (n, newsize):
                self.prefs.append( ["Placeholder_" + str(i+1)] )
            self.teamCount += 1
                
    def swap (self, i, j):
        self.log(3, "swap %d / %d  folks: %s" % (i, j, str(self.folks)))
        x = self.folks[i]
        self.folks[i]=self.folks[j]
        self.folks[j]=x


    def teamFromSpot(self, spot):
        self.log(2,"teamFromSpot spot: %d" % spot)
        team = spot // self.teamsize
        return team


    def pick2SpotsAndteams (self):
        r1 = random.randint(0, len(self.prefs)-1)
        r2 = random.randint(0, len(self.prefs)-1)
        t1 = self.teamFromSpot(r1)
        t2 = self.teamFromSpot(r2)
        return (r1, r2, t1, t2)

    
    def randomSwap (self):
        r1 = random.randint(0, len(self.folks)-1)
        r2 = random.randint(0, len(self.folks)-1)
        self.swap(r1, r2)
        return (r1, r2)


    def score_pref (self, spot, spot2, aList):
        if (spot == spot2):
            return 0
        person1 = aList[spot]
        person2 = aList[spot2]
        if (person1 == 0):
            return 0
        if (person2 == 0):
            return 0

        self.log(2, "score_pref spot1: %d  spot2: %d  list: %s" % (spot, spot2, str(aList)))

        self.log(2, " person1: %d  person2: %d  prefs: %s " % (person1, person2, str(self.prefs)))
        myprefs = self.prefs[person1 - 1]

        self.log(3, "  score_pref spots: %d-%d  persons %d-%d  aList.len: %d  prefs.len: %d" % (spot, spot2, person1, person2, len(aList), len(myprefs )))
        for n in range(0, len(myprefs)-1):
            self.log(3, "  trying spots: %d-%d  persons: %d-%d  n: %d  aList.len: %d" % (spot, spot2, person1, person2, n, len(aList) ))
            if self.prefs[ person1-1 ][n+1] == person2:
                self.log(3, "  score_pref spots %d-%d  persons: %d-%d  RATES %d (%d th)" % (spot, spot2, aList[spot], person2, self.rank[n], n))
                return self.rank[n]
        self.log(3, "  score_pref returns spots: %d-%d  absent persons: %d-%d RATES 0" % (spot, spot2, person1, person2))
        return 0

    def score_one(self, spot, aList):
        self.log(3, "score_one spot: %d  list: %s " % (spot, str(aList)))
        offset = spot % self.teamsize
        start = spot - offset
        self.log(4, " score_one %d start: %d off: %d list: %s" % (spot, start, offset, str(aList)))
        # self.log(4, " score_one %d start: %d off: %d prefs: %s rank: %s list: %s"
        #        % (spot, start, offset, str( self.prefs[ self.folks[spot]-1 ]), str(self.rank), str(aList)))

        myteam = []
        for xx in range (0, self.teamsize):
            myteam.append ( aList[start + xx] )

        # self.log(4, " score_one %d start: %d off: %d team: %s prefs: %s rank: %s"
        #        % (spot, start, offset, str(myteam), str( self.prefs[ self.folks[spot]-1 ]), str(self.rank)))

        pts = 0
        for i in range (0, len(myteam)):
            pts += self.score_pref( spot, start + i, aList)
        return pts


    # team: zero based
    # aList: 
    def score_team(self, team, aList):
        (score, team) = self.score_team_zeros(team, aList)
        return score


    def score_team_zeros(self, team, aList):
        self.log(3, "score_team_zeros")
        sum = 0
        score = 0
        zeros = 0
        for i in range(0, self.teamsize):
            n = (team * self.teamsize) + i
            self.log(4,"score_team calling score_one %d %s" % (n, str(aList)))
            score = self.score_one( n, aList )
            if score == 0:
                zeros += 1
            sum += score
        return (sum, zeros)

    def score_all_zeros(self, aList):
        self.log(3, "score_all_zeros list: %s" % str(aList))
        total = 0
        zeros = 0
        for n in range(0, len(aList)):
            newscore = self.score_one(n, aList)
            if newscore == 0:
                zeros += 1            
            total = total + newscore
            self.log(3,"score_all_zeros loop: %d  adding: %d  new score is: %d" % (n, newscore, total))
        return (total, zeros)


    def score_all(self, aList):
        self.log(2,"score_all")
        total = 0
        for n in range(0, len(aList)):
            newscore = self.score_one(n, aList)
            total = total + newscore
            self.log(3,"score_all %d adding %d now %d" % (n, newscore, total))
        return total


    def score_pp(self, aList):
        self.log(3,"score_pp")
        total = 0
        print ("score_pp Folks: %s", self.folks)
        for n in range(0, len(aList)):
            newscore = self.score_one(n, aList)
            print("%2d %d %s" % (n+1, newscore, self.prefs[n]))
            total = total + newscore
        print ("Total: %d" % total)
        return total


    def reportFolks(self):
        print("%d %s" % ( self.score_all(self.folks), str(self.folks)))


    def reportOtherFolks(self, folks):
        print("%d %s" % ( self.score_all(folks), str(folks)))


    def reportSomePrefs(self, i1, i2):
        for i in range(i1, i2):
            print ( str( self.prefs[i] ))


    def reportPrefs(self):
        self.reportSomePrefs(0, len( self.prefs ))


    def reportTeamsZeros(self, aList):
        self.log(1,"reportTeamsZeros teamCount: %d" % self.teamCount)
        tp=[]
        for n in range(0, self.teamCount):
            (score, zeros) = self.score_team_zeros(n, aList)
            tp.append( (score, zeros) )
        return tp


    def reportTeams(self, aList):
        tp=[]
        for n in range(0, self.teamCount):
            tp.append( self.score_team(n, aList)  )
        return tp


    def pprint(self, aList):
        for i in range(0, len(self.folks)):
            if i % self.teamsize == 0:
                print()
                team = self.teamFromSpot( i )
                (score, zeros)= self.score_team_zeros(team, aList)
                print("Team %d Score: %2d %d zeros " % (team, self.score_team( team, aList), zeros), end='')

                # print( "pprint %i teams(): %d" % (i, teams[i] ))
            print( ("%d %s (%d)\t" % (aList[i] ,self.prefs[ aList[i]-1 ][0], self.score_one(i, aList))), end='')
        print()


    def pprint2(self, aList):
        totalScore = 0
        lowteam = 999;
        highteam = 0
        for i in range(0, len(self.folks)):
            if i % self.teamsize == 0:
                print()
                team = self.teamFromSpot( i )
                (score, zeros) = self.score_team_zeros( team, aList)
                totalScore += score
                if score < lowteam:
                    lowteam = score
                if score > highteam:
                    highteam = score
                print("Team %d (%2d) %d zeros " % (team, score, zeros))

                # print( "pprint %i teams(): %d" % (i, teams[i] ))

            print( ("%2d (%2d) %s %s\t" % (aList[i],
                                           self.score_one(i, aList),
                                           self.prefs[ aList[i]-1 ][0],
                                           str(self.prefs[ aList[i]-1 ] ))))
            # print( ("%2d (%2d) %s\t" % (aList[i],
            #                                self.score_one(i, aList),
            #                                self.prefs[ aList[i]-1 ][0])) )


        print("\nScore: %d  Teamsize: %d Mean: %d High: %d Low %d" % (totalScore, self.teamsize, totalScore / ((len(self.folks) / self.teamsize)+1), highteam, lowteam))


    def pprint3(self, aList):
        totalScore = 0
        lowteam = 999;
        highteam = 0
        for i in range(0, len(self.folks)):
            if i % self.teamsize == 0:
                print()
                team = self.teamFromSpot( i )
                (score, zeros) = self.score_team_zeros( team, aList)
                totalScore += score
                if score < lowteam:
                    lowteam = score
                if score > highteam:
                    highteam = score
                print(("Team %d: " % (team+1)), end="")

            print( ( "%s, " % (self.prefs[ aList[i]-1 ][0]) ), end="")
        self.printCmdLineCalc()

    def printCmdLineCalc (self):
        ss = str(self.super_folks).replace("[","\"").replace("]","\"")
        print("\n\nTo recalculate:\npython3 buckets-no-zeros.py -t %d --calc %s < prefsfile" % (self.teamsize, ss ) )

    def ranksFromPrefs(self, record):
        return record[1:]


    def printPrefs(self):
        for i in range(0, 32):
            print ("%s, " % names[i], end='')
            for j in range(0,6):
                print(" %s," % names[ prefs[i][j]-1 ], end='' )
                print()

    def starting(self):
        self.start_time = time.time()
        print ( "\nStart: %s" % str(datetime.datetime.now() ))

    def stopping(self):
        end_time = time.time()
        seconds = end_time - self.start_time
        print ("End: %s" % str(datetime.datetime.now() ))
        print ("Runtime: %d seconds for %d generations" % (seconds, self.generations))

    def arrange(self):
        # should do something smarter for initial arrangement?
        self.log(2,"arrange")
        self.setupFolks()

    def cache_score(self, new_score):
        if new_score < 0:
            new_score = self.score_all(self.folks)
            self.max_score = new_score
            self.keepit = self.folks[:]
        if self.max_score > self.super_score:
            self.super_score = self.max_score
            self.super_folks = self.keepit[:]
            self.super_exchanges = self.exchanges
            self.scorenow('Max', self.super_folks, self.exchanges, self.nixedExchanges)

    def planbyo(self):
        r = ""
        if self.planb:
            r = "(Plan B)"
        return r

    def shallWeBegin(self):
        self.log(2,"shallWeBegin")
        self.starting()
        self.arrange();
        print("\nMr. Blee's Fabulous Olde Team Picker %s" % self.planbyo())
        random.seed( self.seed )

    def goodTrade(self, zeros_before1, zeros_before2, zeros_after1, zeros_after2):
        d1 = zeros_before1 - zeros_after1
        d2 = zeros_before2 - zeros_after2
        delta = abs(zeros_after1 - zeros_after2)

        # nix wide swings
        if delta > 2: 
            return False

        # otherwise, if either is moving in the right direction, go
        if (d1 >= 0) and (d2 >= 0):
            return True
        
        self.log(1,"goodTrade FF Team 1: %d->%d Team 2: %d->%d (%d %d) " % (zeros_before1, zeros_after1, zeros_before2, zeros_after2, d1, d2))
        return False

    def shouldOveride(self):
        return random.randint(0,100) < self.overidePercent

    def exchangeMaybe(self):
        self.log(2,"exchangeMaybe")
        if self.planb:
            self.exchangeMaybePlanB()
        else:
            self.exchangeMaybePlanA()

    def exchangeMaybePlanB(self):
        self.log(2,"exchangeMaybePlanB")
        (spot1, spot2, team1, team2) = self.pick2SpotsAndteams()

        (before1, zeros_before1) = b.score_team_zeros(team1, b.folks)
        (before2, zeros_before2) = b.score_team_zeros(team2, b.folks)
        self.swap(spot1, spot2)
        (after1, zeros_after1)= b.score_team_zeros(team1, b.folks)
        (after2, zeros_after2)= b.score_team_zeros(team2, b.folks)

        self.exchanges += 1
        improved = (after1 + after2) - (before1 + before2)
        if (improved > 0) and self.goodTrade(zeros_before1, zeros_before2, zeros_after1, zeros_after2):
            self.cache_score(-1)
            # new_score = current_score + improved
            # current_score = new_score
            self.log(2,"  improved %d" % (improved))

        else:
            # but wait, perhaps we should do it anyway...
            if self.shouldOveride():
                self.log(2,"overiding improved: %d delta: %d" % (improved, self.delta))
                self.countOverides += 1
            else:
                #undo previous swap
                self.nixedExchanges += 1
                self.swap(spot1, spot2)
                self.exchanges -= 1

        self.current_score = self.score_all(self.folks)
        
    def exchangeMaybePlanA(self):
        self.log(2,"exchangeMaybePlanA")
        ij = self.randomSwap()
        new_score = self.score_all(self.folks)
        if new_score > self.max_score:
            self.cache_score(new_score)
        if (new_score < self.max_score):
            # allow suboptimal some of the time
            if ((self.overidePercent > 0) and self.shouldOveride()):
                # self.log(-1, "(%d  %d)" % (self.overide, (self.max_score- new_score)))
                self.log(2, "Overide")
                self.log(2, "%d %s %d" % (self.max_score, str(self.folks), self.countOverides))
                self.countOverides += 1
            else:
                # undo the swap
                self.log(2, "Undo %d:  %d vs %d  %s" % (self.generations, new_score, self.max_score, str(ij)))
                self.swap( ij[0], ij[1])

    def run(self):
        self.log(2,"\nrun")
        self.readStdIn()
        self.shallWeBegin()
        for i in range(0, self.loops):
            self.runit()
        self.stopping()

        print("Best %d: %s over: %d" % ( self.super_score, str(self.super_folks), self.countOverides))
        self.pprint2(self.super_folks)
        self.pprint3(self.super_folks)

    def breadcrumbdots(self):
        if self.breadcrumbs > 0:
            if (gen % 10000 == 0):
                print( ".", end='', flush=True)
                
    def scorenow(self, title, alist, swaps, nixed):
        (t, z) = self.score_all_zeros(alist)
        print("%s %d (%d): %s swaps: %d (%d)" % (title, t, z, str (alist), swaps, nixed))

    def runit(self):
        n = 0
        self.countOverides = 0
        self.log(1,"run starting with %d folks: %s" % (len(self.folks), str(self.folks)))
        self.cache_score(-1)
        self.log(1,"\nYoYo %s" % self.reportTeamsZeros( self.folks ))

        current_score = self.score_all(self.folks)

        for gen in range(0, self.generations):
            new_score = 0
            self.exchangeMaybe()
            self.breadcrumbdots()

            self.log(2, ("Gen: %d Best %d Teamscores %s %s "
                         % (gen, self.max_score,
                            str( self.reportTeamsZeros( self.folks )),
                            str( self.folks))))
            
if __name__ == '__main__':
    in_overide = 1
    in_delta = 5
    in_generations = 1000
    in_loops = 5
    in_breadcrumbs = 0
    in_prefs = "prefs.txt"
    in_teamsize = 4
    in_loglevel = 0
    in_score = False
    in_planb = False
    in_seed = None
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--random", help="supply a random seed for repeatability")
    parser.add_argument("-a", "--alternate", help="plan b.", action="store_true")
    parser.add_argument("-s", "--score", help="send in string of comma-separated ints.", action="store_true")
    parser.add_argument("-t", "--teamsize", help="maximum size of teams, default is 4.")
    parser.add_argument("-o", "--overide", help="how often to allow worse generations, default is 1 %.")
    parser.add_argument("-d", "--delta", help="delta - minimum difference, default is 5.")
    parser.add_argument("-g", "--generations", help="generations - default is 1000.")
    parser.add_argument("-l", "--loops", help="how many iterations of generations, default is 1.")
    parser.add_argument("-v", "--verbose", help="log level, default is 0.")
    parser.add_argument("-p", "--prefs", help="file name for preferences, e.g. Mr Bubba,3,4,19,20. default is prefs.txt")
    parser.add_argument("-b", "--breadcrumbs", help="iterations for each timer ticks . to see progress, default is 0 to skip")
    parser.add_argument("-c", "--calc", help="pprint a given order")
    
    args = parser.parse_args()
    if args.verbose:
        in_loglevel = int(args.verbose)

    if args.random:
        in_seed = args.random

    if args.alternate:
        in_planb = args.alternate

    if args.teamsize:
        in_teamsize = int(args.teamsize)

    if args.overide:
        in_overide = int(args.overide)

    if args.delta:
        in_delta = int(args.delta)

    if args.generations:
        in_generations = int(args.generations)

    if args.loops:
        in_loops = int(args.loops)

    if args.prefs:
        in_prefs = args.prefs

    if args.breadcrumbs:
        in_breadcrumbs = int(args.breadcrumbs)

    b = Buckets( in_teamsize, in_loops, in_generations, in_delta, in_overide, in_breadcrumbs, in_loglevel, in_planb, in_seed )

    if args.calc:
        b.readStdIn()
        x = args.calc.split(',')
        mylist = [ (int(zz)) for zz in x]
        print("calc list: %s" % str(mylist))
        b.reportOtherFolks(mylist)

        print("now %s" % str( b.reportTeamsZeros( mylist )))
        b.pprint2(mylist)
        exit()
        
    if args.score:
        b.readStdIn()
        # mm = [19, 23, 21, 11, 3, 9, 24, 12, 29, 25, 17, 18, 8, 26, 5, 27, 32, 28, 4, 2, 7, 14, 10, 13, 30, 22, 31, 1, 15, 20, 16, 6]
        # mm = [2, 29, 8, 26, 24, 32, 19, 21, 18, 15, 12, 9, 13, 16, 7, 20, 11, 23, 1, 10, 25, 6, 14, 17, 28, 4, 27, 5, 30, 3, 31, 22]
        # mm = [4, 3, 27, 30,  16, 28, 13, 5,  1, 25, 26, 7,  14, 19, 15, 31,  12, 6, 17, 11,  0, 10, 21, 29,  22, 18, 23, 20,  8, 9, 2, 24]
        mm = [5, 4, 28, 31,  17, 29, 14, 6,  2, 26, 27, 8,  15, 20, 16, 32,  13, 7, 18, 12,  1, 11, 22, 30,  23, 19, 24, 21,  9, 10, 3, 25]
        # mm = [7, 16, 20, 13, 25, 18, 26, 30, 31, 11, 23, 1, 12, 15, 27, 9, 10, 19, 21, 24, 14, 28, 17, 29, 6, 22, 32, 3, 5, 8, 2, 4]
        # [26, 10, 8, 27, 32, 24, 18, 19, 13, 16, 20, 7, 31, 29, 12, 17, 30, 6, 3, 21, 5, 2, 4, 28, 1, 25, 11, 14, 15, 23, 9, 22]
        b.reportOtherFolks(mm)
        for i in range(0, 7):
            print("team %d %d" % (i, b.score_team(i, mm)))
            exit()

    else:
        b.run()
