"""Thirty-three ending scores, expressed in fractions of a reserved ending span."""
def finish_piece(s):
 k=s.k;a=s.ending_start;d=s.duration-a;s.notes=[n for n in s.notes if n['start']<a-.03]
 for n in s.notes:n['duration']=min(n['duration'],a-n['start']-.012)
 raw=s.raw(a);c=s.chord(a,k)
 def h(j,t,length,p,v=35,inst=None):return s.add('ending-'+str(j),s.palette[(k+j*7)%len(s.palette)] if inst is None else inst,a+t*d,length*d,p,v,'ending: '+s.ending)
 def p(target):return s.pitch(a,target)
 def voice(j,t,length,pitch,vowel='o',breath=False):
  z=h(j,t,length,pitch,35-j,97+j%4)
  if z:z['vocal']={'vowel':vowel,'syllable':'mu','register':j%4,'air':.022,'breath_only':breath}
  return z
 if k==0:
  for j in range(7):
   for q in range(4-j//2):h(j,.06*j+.15*q,.14,p(51+j*6+q*2),33+j%3)
  for j,target in enumerate([55,62,69,76]):h(10+j,.69+j*.02,.28-j*.02,p(target),32, [12,71,33,19][j])
 elif k==1:
  for j in range(4):h(j,j*.12,.16,p(61+j*5),35-j)
  h(7,.71,.2,p(88),32,74)
 elif k==2:
  for j in range(5):h(0,j*.15,.13,p(55+[0,7,4,7,0][j]),35,12)
  for j in range(3):h(j+1,j*.11,.3,p(72+j*5),30)
  h(0,.85,.12,p(55),35,12)
 elif k==3:
  for rep in range(2):
   for j in range(4):
    if rep==1 and j==2:continue
    h(j,rep*.46+j*.09,.07,p(61+j*6),34,[12,19,71,33][j])
 elif k==4:
  for j,q in enumerate(reversed(c*2)):h(j,.05+j*.08,.21,q,36-j%4)
 elif k==5:
  h(0,0,.12,c[-1],32,74);h(1,.75,.09,c[0],28,51)
 elif k==6:
  root=min(raw,key=lambda x:abs(x-65));fifth=min(raw,key=lambda x:abs(x-root-7.01955))
  voice(0,0,.54,root,'a');voice(1,.04,.5,root,'o');voice(0,.60,.36,root,'u');voice(1,.62,.34,fifth,'e')
 elif k==7:
  for j in range(4):h(0,j*.12,.09,c[j%len(c)],35,12);h(1,.49+j*.12,.09,c[-1-j%len(c)],35,71)
 elif k==8:
  for j in range(4):h(j,j*.04,.4,p(51+j*9),33,[48,71,12,74][j]);h(j,.53+j*.03,.43-j*.03,p(65+(1 if j%2 else -1)*(j+1)),32,[48,71,12,74][j])
 elif k==9:
  pool=s.pool(a);ix=min(len(pool)-2,min(range(len(pool)),key=lambda z:abs(pool[z]-73)));t=0;step=.018;q=0
  while t<.84:h(0,t,step*.86,pool[ix+q%2],34,15);t+=step;step*=1.11;q+=1
  h(0,.87,.1,pool[ix],34,15)
 elif k==10:
  for j,q in enumerate([53,57,60,65]):h(j,.06+j*.012,.34,q,35,8)
  for j,q in enumerate([48,60,64,67,72]):h(10+j,.53+j*.012,.42-j*.012,q,35,8 if j%2 else 48)
 elif k==11:h(0,.05,.30,p(83),34,19)
 elif k==12:
  for j in range(4):h(j,.04+j*.05,.88-j*.05,c[j%len(c)],29,[12,48,19,33][j])
  for j in range(4):h(5,j*.13,.10,p(74+j*2),37,71)
 elif k==13:
  for j in range(4):h(j,j*.13,.11,p(66+j*5),36-j)
  h(7,.74,.2,p(50),35,41)
 elif k==14:
  for j in range(4):
   z=h(j,j*.1,.42,c[j%len(c)],35,[12,71,33,19][j])
   if z:z['effect']={'type':'reverse_grains','grain_seconds':max(.1,z['duration']),'wet':1.,'delay':.12,'feedback':.2,'reverse_envelope':True}
  h(9,.72,.24,c[0],34,12)
 elif k==15:
  root=p(70)
  for j in range(5):h(j,j*.035,.65-j*.035,root,31,[12,71,19,33,7][j])
  h(8,.74,.22,p(75),32,74)
 elif k==16:
  for j in range(3):h(j,j*.17,.12,p(62+[0,3,8][j]),34-j, [71,12,74][j])
 elif k==17:
  cell=[p(60),p(67),p(73),p(69)]
  for rep in range(4):
   for j,q in enumerate(cell[rep:]):h(j,rep*.24+j*.045,.07,q,35,12 if j%2 else 71)
 elif k==18:
  for j in range(5):h(j,j*.08,.3,p(60+j*5),33-j)
  h(9,.83,.11,p(50),35,41)
 elif k==19:
  for j in range(8):
   t=j*.015;end=.22+j*.09
   while t<end:h(j,t,min(.08,end-t),p(50+j*6),33);t+=.13
 elif k==20:
  cell=[(0.,.09,61),(.14,.05,77),(.22,.1,68),(.36,.06,84)]
  for j,(t,length,q) in enumerate(cell):h(j,t,length,p(q),34,[12,71,33,6][j])
  for j,(t,length,q) in enumerate(reversed(cell)):h(4+j,.55+.42-t-length,length,p(q),34,[6,33,71,12][j])
 elif k==21:h(0,0,.68,c[0],33,71);h(1,.025,.94,c[-1],31,12)
 elif k==22:
  for j in range(9):h(j%2,j*.063,.058,p(65+[0,2,4,1,5,3,7,4,9][j]),38-j%3,71 if j%2 else 33)
  h(9,.72,.24,p(90),32,74)
 elif k==23:
  for j in range(8):h(0,j*.10,.085,p(53+[0,7,4,7,0,4,7,0][j]),35,12)
  for j in range(4):h(j+1,.03+j*.18,.2,c[j%len(c)],31,[71,48,74,19][j])
  h(8,.88,.09,c[-1],34,71)
 elif k==24:
  for j in range(5):h(0,j*.1,.09,p(75+j%3*3),38,71)
  h(3,.57,.16,c[0],31,12);h(0,.80,.13,p(83),38,71)
 elif k==25:
  target=p(71)
  for j in range(6):
   z=h(j,j*.025,.94-j*.025,target,33,[46,48,71,74,33,0][j])
   if z:z['gliss']={'to_pitch':p(target+(j-2.5)*3),'shape':'smoothstep','arrive_fraction':.9,'endpoints_are_field_members':True}
 elif k==26:
  for j in range(4):h(0,j*.1,.085,p(60+j*4),35,33)
  for j,q in enumerate(c):h(4+j,.58+j*.025,.37-j*.025,q,31,[12,71,19,7][j%4])
 elif k==27:
  for j in range(4):
   z=h(j,j*.035,.72-j*.035,c[j%len(c)],37,[33,12,71,19][j])
   if z:z['effect']={'type':'multitap','delay':.23+j*.09,'feedback':.5,'wet':.8,'excitation_seconds':.7}
  h(8,.89,.07,c[0],34,33)
 elif k==28:
  cell=[p(62),p(69),p(74),p(67)]
  for j,q in enumerate(cell):h(j,j*.06,.045,q,35,12)
  for j,q in enumerate(cell):h(j,.34+j*.12,.09,q,35,12)
  h(9,.89,.08,p(71),32,74)
 elif k==29:
  for j in range(4):voice(j,j*.02,.42+j*.12,p(59+j*6),['a','e','o','u'][j])
  voice(0,.84,.11,p(65),'u',True)
 elif k==30:
  for j in range(5):h(j,j*.055,.72-j*.055,c[j%len(c)],31+j)
  h(9,.76,.09,c[-1],39,71)
 elif k==31:
  first=s.notes[:10]
  for j,z in enumerate(first[:-1]):h(j,.02+j*.08,.09,p(144-z['pitch']),z['velocity']-3,s.palette[(j*9)%len(s.palette)])
 elif k==32:
  for j,q in enumerate(c):h(j,.03+j*.025,.4,q,31,[12,48,19,33][j%4])
  for j,q in enumerate([p(77),p(81),p(74),p(79)]):h(9,.50+j*.11,.09 if j<3 else .13,q,36-j,71)
 s.scenes.append(dict(start=a,end=s.duration,texture='ending: '+s.ending,start_beat=s.bt(a),end_beat=s.nbeats,ensemble=sorted(set(n['instrument'] for n in s.notes if n['start']>=a)),section_level=35,form='composed ending'))
