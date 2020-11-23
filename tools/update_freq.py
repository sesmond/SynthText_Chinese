from collections import Counter
import pickle
cnt=0
filename = '../data/data/newsgroup/newsgroup.txt'
with open(filename) as f:
    c = Counter()
    for x in f:
        # x=x.decode('utf-8')
        c += Counter(x.strip())
        cnt+=len(x.strip())
        print (c)
print (cnt)

# 这是个json文件，然后用二进制格式写进去了。。我真是醉了。艹。
for key in c:
    c[key]=float(c[key])/cnt  
    print (key,c[key])
     
d = dict(c)
#print d
with open("../char_freq.cp", 'wb') as f:
    pickle.dump(d,f)


# 把文章中字符出现的概率记录在这个文件里