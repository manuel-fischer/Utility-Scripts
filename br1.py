# bulk rename prepare
import sys, os

hash_func = lambda x: hash(x) & 0xffff

"""
def build_lst(pr, path, indent, counter):
    lst = os.listdir(path)
    for fn in lst:
        pr(f"{indent}[{counter():04x}] {fn}")
        el_path = os.path.join(path, fn);
        if os.path.isdir(el_path):
            build_lst(pr, el_path, indent+"    ", counter)
"""            

def build_lst(pr, path, disppath, indent, counter):
    lst = os.listdir(path)
    for fn in lst:
        p = os.path.join(disppath, fn) if disppath else fn
        pr(f"{counter():04d}    {p}")
        el_path = os.path.join(path, fn);
        if os.path.isdir(el_path):
            build_lst(pr, el_path, p, indent+"    ", counter)

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    i = 0
    def counter():
        global i
        i+=1
        return i
    
    
    with open("_br-org.txt", "w") as fo, open("_br-new.txt", "w") as fw:
        def pr(*a, **kv):
            print(*a, **kv, file=fo)
            print(*a, **kv, file=fw)
        build_lst(pr, path, None, "", counter)
        
    
    
if 0:
    
    lst = os.listdir()
    ids = [None] * len(lst)
    for i, fn in enumerate(lst):
        h = hash_func(fn)
        while h in ids:
            h = (h+i) & 0xffff
        ids[i] = h

    assert(len(ids) == len(set(ids)))
        
    
    ren_ss = "\n".join(f"{id:04x}    {fn}" for id, fn in zip(ids, lst))
    with open("_br-org.txt", "w") as fo, open("_br-new.txt", "w") as fw:
        fo.write(ren_ss)
        fw.write(ren_ss)
    
