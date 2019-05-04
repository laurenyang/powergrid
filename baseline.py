import util

def baseline(d,t,w,s,b,p):
  if w + s > d:
    if w > d:
      return ((t,[('W','D',d),('W','B',w-d),('S','B',s),('P','B',p)]),(t+1,[('W','D',d),('W','B',w-d),('S','B',s),('P','B',p)]),(t+2,[('W','D',d),('W','B',w-d),('S','B',s),('P','B',p)]))
    if w == d:
      return ((t,[('W','D',d),('S','B',s),('P','B',p)]),(t+1,[('W','D',d),('S','B',s),('P','B',p)]),(t+2,[('W','D',d),('S','B',s),('P','B',p)]))
    return ((t,[('W','D',w),('S','D',d-w),('S','B',w+s-d),('P','B',p)]),(t+1,[('W','D',w),('S','D',d-w),('S','B',w+s-d),('P','B',p)]),(t+2,[('W','D',w),('S','D',d-w),('S','B',w+s-d),('P','B',p)]))
  if w + s == d:
      return ((t,[('W','D',w),('S','D',s),('P','B',p)]),(t+1,[('W','D',w),('S','D',s),('P','B',p)]),(t+2,[('W','D',w),('S','D',s),('P','B',p)]))
  if util.isDay(t):
    return ((t,[('W','D',w),('S','D',s),('P','D',d-s-w),('P','B',p+s+w-d)]),(t+1,[('W','D',w),('S','D',s),('P','D',d-s-w),('P','B',p+s+w-d)]),(t+2,[('W','D',w),('S','D',s),('P','D',d-s-w),('P','B',p+s+w-d)]))
  if w+b>=d:
    return ((t,[('W','D',w),('B','D',d-w),('P','B',p)]),(t+1,[('W','D',w),('B','D',d-w),('P','B',p)]),(t+2,[('W','D',w),('B','D',d-w),('P','B',p)]))
  return ((t,[('W','D',w),('B','D',b),('P','D',d-b-w),('P','B',p+b+w-d)]),(t+1,[('W','D',w),('B','D',b),('P','D',d-b-w),('P','B',p+b+w-d)]),(t+2,[('W','D',w),('B','D',b),('P','D',d-b-w),('P','B',p+b+w-d)]))