from collections import defaultdict

if __name__ == '__main__':
    pool = {
        52: ["Test1"],
        53: ["Test2", "Test3"]
    }

    dd = list(set(pool.keys()))
    dd.sort()
    selected = list(pool[dd[1]])
    selected.reverse()
    print(selected)
    for n in selected:
        print(n)
