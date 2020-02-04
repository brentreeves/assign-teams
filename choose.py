# choose.py
# Tomohiro Oda
# input format:
# Blee(1)   means Blee has no preference but must be on some team
# Blee(1):Blah(9)  means Blee wants Blah on their team very much
# Blee(1):Blah(9):Blue(5)  means Blee wants Blah on their team very much, and Blue a medium bit
#
class Family:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.likes = {}.copy()

class Group:
    def __init__(self, max_size):
        self.max_size = max_size
        self.current_size = 0
        self.families = []
        self.score = 0
    def add_family(self, new_family):
        if self.current_size + new_family.size > self.max_size:
            return None
        for family in self.families:
            if  new_family.name in family.likes :
                self.score = self.score + family.likes[new_family.name]
            if family.name in new_family.likes:
                self.score = self.score + new_family.likes[family.name]
        self.current_size = self.current_size + new_family.size
        self.families = self.families + [new_family]
        return new_family
    def remove_family(self, rejected_family):
        if rejected_family not in self.families:
            return None
        for family in self.families:
            if family is not rejected_family:
                if rejected_family.name in family.likes:
                    self.score  = self.score - family.likes[rejected_family.name]
                if family.name in rejected_family.likes:
                    self.score  = self.score - rejected_family.likes[family.name]
        self.current_size  = self.current_size - rejected_family.size
        self.families = self.families+[]
        self.families.remove(rejected_family)
        return rejected_family
    def printout(self):
        if len(self.families) == 0:
            print ("")
        else:
            string = self.families[0].name
            for family in self.families[1:]:
                string = string + ", %s" % (family.name)
            print (string)
    def copy(self):
        new_group = self.__class__(self.max_size)
        new_group.current_size = self.current_size
        new_group.families = self.families
        new_group.score = self.score
        return new_group


class ScoreBoard:
    def __init__(self, size):
        self.size = size
        self.board = []
    def add(self, item, score):
        if len(self.board) == self.size and self.board[-1][1] > score:
            return None
        index = 0
        while index < len(self.board) and self.board[index][1] > score:
            index = index + 1
        self.board = self.board[:index]+[(item, score)]+self.board[index:]
        if len(self.board) >= self.size:
            self.board = self.board[:self.size]
        return (item, score)
    def printout(self):
        for index in range(0, len(self.board)):
            groups, score = self.board[index]
            print ("Plan %d: score %d" % (index + 1, score))
            for group_index in range (0, len(groups)):
#                print "------ Group %d ------" % (group_index + 1)
                print ("Group %d (%d):" % (group_index + 1, groups[group_index].current_size),groups[group_index].printout())
            print ("")


class GroupArranger:
    def __init__(self, num_groups, max_group_size, size_of_output = 20):
        self.num_groups = num_groups
        self.max_group_size = max_group_size
        self.size_of_output = size_of_output


    def _recursive_arrange(self, families, family_index, max_group_index, groups, scores):
        if family_index == len(families):
            new_groups = []
            score = 0
            for group in groups:
                new_groups = new_groups + [group.copy()]
                score = score + group.score
            scores.add(new_groups, score)
            return scores
        family = families[family_index]
        for group_index in range(0, min(len(groups), max_group_index+ 1)):
            group = groups[group_index]
            if group.add_family(family) is not None:
                self._recursive_arrange(families, family_index + 1, max(group_index + 1, max_group_index), groups, scores)
                group.remove_family(family)
        return scores


    def arrange(self, families):
        groups = []
        for index in range(0, self.num_groups):
            groups = groups + [Group(self.max_group_size)]
        scores = ScoreBoard(self.size_of_output)
        self._recursive_arrange(families, 0, 0, groups, scores)
        for group in groups:
            if group.score != 0:
                print ("Scoring Error : %d" % (group.score))
            if len(group.families) != 0:
                print ("add/remove Error")
        return scores


    def parse_family(self, line):
        def parse_entry(header):
            items = header.split('(')
            return (items[0], int(items[1].split(')')[0]))
        entries = line.split(':')
        name, size = parse_entry(entries[0])
        family = Family(name, size)
        for entry in entries[1:]:
            name, friendness = parse_entry(entry)
            family.likes[name] = friendness
        return family
            
    def arrange_from_file(self, filename):
        file = open(filename, "r")
        lines = file.readlines()
        file.close()
        families = []
        for line in lines:
            if (line[:1] != "#"):
                families = families + [self.parse_family(line)]
        return self.arrange(families)


if __name__ == '__main__':
    import sys
    args = sys.argv
    if len(args) != 4:
        print ("Usage: %s <number of groups> <max group size> <filename>" % (args[0]))
        num_groups = 2
        max_group_size = 3
        filename = "c:\data\projects\python\teams-p2.txt"
        group_arranger = GroupArranger(num_groups, max_group_size)
        result = group_arranger.arrange_from_file(filename)
        result.printout()
    else:
        num_groups = int(args[1])
        max_group_size = int(args[2])
        filename = args[3]
        group_arranger = GroupArranger(num_groups, max_group_size)
        result = group_arranger.arrange_from_file(filename)
        result.printout()
