import sys
import re

trace = False
if trace:
    def print_cache(cache, action):
        lc = len(cache)
        for row in range(lc):
            for col in range(len(cache[row])):
                print(f"{cache[row][col]} ({action[row][col]})", end = ' ')
            print()
else:
    def print_cache(*args):
        pass

def read_file(filepath):
    lines = []
    if filepath:
        with open(filepath,  'r') as f:
            lines = f.read().splitlines()
    else:
        print("Filepath not provided")
        return None

    return lines

def lev_distance(line1, line2):
    cache = []
    action = []

    l1 = len(line1) #length of line1
    l2 = len(line2) #length of line2

    IGNORE = 'I'
    REMOVE = 'R'
    ADD = 'A'

    for _ in range(l1 + 1):
        cache.append([0] * (l2 + 1))
        action.append(['-'] * (l2 + 1))

    cache[0][0] = 0
    action[0][0] = IGNORE

    for i1 in range(1, l1 + 1):
        i2 = 0
        cache[i1][i2] = i1
        action[i1][i2] = REMOVE

    for i2 in range(1, l2 + 1):
        i1 = 0
        cache[i1][i2] = i2
        action[i1][i2] = ADD

    #skipping substitute as we need only (add and remove) for diff 
    for i1 in range(1, l1 + 1):
        for i2 in range(1, l2 + 1):
            a = cache[i1][i2-1] + 1
            r = cache[i1-1][i2] + 1
            minimum = min(a, r)

            if line1[i1-1] == line2[i2-1]:
                cache[i1][i2] = cache[i1-1][i2-1]
                action[i1][i2] = IGNORE
                continue
            else:
                if minimum == a:
                    cache[i1][i2] = a
                    action[i1][i2] = ADD
                else:
                    cache[i1][i2] = r
                    action[i1][i2] = REMOVE

    print_cache(cache, action)

    patch = []
    while l1 >= 0 and l2 >= 0:
        if action[l1][l2] == ADD:
            l2 -= 1 
            patch.append((ADD, l2, line2[l2]))
        elif action[l1][l2] == REMOVE:
            l1 -= 1
            patch.append((REMOVE, l1, line1[l1]))
        else:
            l1 = l1-1
            l2 = l2-1

    patch.reverse()
    
    return patch

PATCH_REGEXP : re.Pattern = re.compile(r"([AR]) (\d+) (.*)")

class Subcommand:
    name: str
    sign: str
    desc: str

    def __init__(self, name, sign, desc):
        self.name = name
        self.sign = sign
        self.desc = desc

    def run(self, program, args):
        assert False, "Not implemented"

class DiffSubcommand(Subcommand):
    def __init__(self):
        super().__init__("diff", "<file1> <file2>", "prints the difference between files")

    def run(self, program , args):
        if len(args) < 2:
            print(f"Usage: {program} {self.name} {self.sign}")
            print("Not enough files were provided")
            return 1

        f1, f2 = args

        lines1 = read_file(f1)
        lines2 = read_file(f2)

        patch = lev_distance(lines1, lines2)

        patch_file_name = f1

        with open(f'{patch_file_name}.patch', 'w') as f:
            for line in patch:
                f.write(line)
                f.write('\n')

        for action, line_no, line in patch:
            print(f"{action} {line_no} ({line})")

        return 0 

class PatchSubcommand(Subcommand):
    def __init__(self):
        super().__init__("patch", "<file> <patch_file.patch>", "patch the file with patch_file.patch")

    def run(self, program, args):
        if args < 2:
            print(f"Usage: {program} {self.name} {self.sign}")
            print("Not enough arguments were provided")

        file_path, patch_file = args

        lines = read_file(file_path).splitlines()
        flag = True
        for row, line in enumerate(read_file(patch_file).splitlines()):
            if len(line) == 0:
                continue

            match = PATCH_REGEXP.match(line)
            if match is None:
                print("Invalid patch")
                flag = False
                continue
            patch.append((match.group(1), int(match.group(2)), match.group(3)))

            if not flag:
                return 1

            for action, line_no, line in reversed(patch):
                if action == ADD:
                    lines.insert(line_no, line)
                elif action == REMOVE:
                    lines.pop(line_no)
                else:
                    assert False, "unreachable"

def main():
    args = sys.argv
    if len(args) < 3:
        print(f"Usage: {args[0]}")
        print("not enough arguments were provided")
        exit(1)

    current_program, subcommand, *args = args

if __name__ == "__main__":
    exit(main())
