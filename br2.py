# bulk rename resolve
import sys, os

"""
def parse_lst(lines):
    ret = []

    cur = None
    cur_el = None
    for l in lines:
        assert (len(l) - len(l.lstrip())) in ([0] + [4]*bool(cur))
        if l[0:4] != "    ":
            l
        else:
            parse_lst(
"""     


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    J = lambda p: os.path.join(path, p)

    with open(J("_br-org.txt"), "r") as fo, open(J("_br-new.txt"), "r") as fw:
        re_lst = []
        for lo, lw in zip(fo.readlines(), fw.readlines()):
            #print(lo, lw)
            assert lo[0:5] == lw[0:5]
            assert lo[4:5] == ' '

            ofn = lo[5:].strip().replace('/', os.path.sep)
            wfn = lw[5:].strip().replace('/', os.path.sep)
            
            re_lst.append([ofn, wfn])
    
    delfiles = []
    
    for i in range(len(re_lst)):
        ofn, wfn = re_lst[i]
        if wfn == "":
            delfiles.append(ofn)
        elif ofn != wfn:
            print(f"RENAME    {ofn}    ->    {wfn}")
            dirpath, _ = os.path.split(wfn)
            if dirpath and not os.path.exists(J(dirpath)):
                os.makedirs(J(dirpath))
            assert not os.path.exists(J(wfn))
            os.rename(J(ofn), J(wfn))
            
            # keep paths
            if 1:
                for j in range(i+1, len(re_lst)):
                    jofn, _ = re_lst[j]
                    if jofn.startswith(ofn) and jofn[len(ofn)] in ["/", "\\"]:
                        re_lst[j][0] = wfn + jofn[len(ofn):]
                        
                for j in range(0, len(delfiles)):
                    jofn = delfiles[j]
                    if jofn.startswith(ofn) and jofn[len(ofn)] in ["/", "\\"]:
                        delfiles[j] = wfn + jofn[len(ofn):]


    delfiles.sort(key=lambda f: -len(f)) # deeper paths first
    for df in delfiles:
        print(f"DELETE    {df}")
        pdf = J(df)
        assert os.path.isdir(pdf)
        assert not os.listdir(pdf)
        os.rmdir(pdf)
        

    os.remove("_br-org.txt")
    os.remove("_br-new.txt")
            
