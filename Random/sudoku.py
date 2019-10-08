from time import time
start=time()
sudokus=[]
with open("unsolved.txt",'r') as f:
    for line in f:
        sudokus.append(line.strip('\n'))

def TIMER(x):
    return '%d min %d sec' %(int(x/60),int(x%60))

def PRINT(S):
    for x in range(9):
        if x%3==0 and x>0: print('---+---+---')
        line=S[9*x:9*x+3]+'|'+S[9*x+3:9*x+6]+'|'+S[9*x+6:9*x+9]
        print(line.replace('-','.'))
    print('')

def align(S):
    ROWS=[]
    COLS=[]
    BLOK=[]
    for x in range(9):
        ROWS.append(S[x*9:(x+1)*9])
        COLS.append(S[x::9])
        y=max(int(x/3)*27-9,0)
        if y==45:y=45-9
        BLOK.append(S[x*3+y:(x+1)*3+y]+S[x*3+9+y:(x+1)*3+9+y]+S[x*3+18+y:(x+1)*3+18+y])
    return ROWS,COLS,BLOK

def LOGIC(S):
    solvable=True
    ROWS,COLS,BLOK=align(S)
    TEMP=S
    options=[]
    change=False
    for row in range(9):
        for col in range(9):
            if ROWS[row][col]=='-':
                block=int(col/3)+3*int(row/3)
                stack='123456789'
                for filled in list(ROWS[row].replace('-','')): stack=stack.replace(filled,'')
                for filled in list(COLS[col].replace('-','')): stack=stack.replace(filled,'')
                for filled in list(BLOK[block].replace('-','')): stack=stack.replace(filled,'')
                if len(stack)==1:
                    change=True
                    S=S[:row*9+col]+stack+S[row*9+col+1:]
                    ROWS,COLS,BLOK=align(S)
                options.append(stack)
            else:
                options.append('X')

    if change==False:
        for x in range(81):
            if len(options[x])==1:
                if options[x]!='X': S=S[:x]+options[x]+S[x+1:]
            else:
                row=int(x/9)
                col=x%9
                block=int(col/3)+3*int(row/3)
                row_options=options[row*9:row*9+9]
                col_options=options[col::9]
                BLOCK_OPTS=[]
                for temp in range(9):
                    y=max(int(temp/3)*27-9,0)
                    if y==45:y=45-9
                    BLOCK_OPTS.append(options[temp*3+y:(temp+1)*3+y]+options[temp*3+9+y:(temp+1)*3+9+y]+options[temp*3+18+y:(temp+1)*3+18+y])
                block_options=BLOCK_OPTS[block]
                row_options.remove(options[x])
                col_options.remove(options[x])
                block_options.remove(options[x])
                for entry in list(options[x]):
                    if all(entry not in R for R in row_options):S=S[:x]+entry+S[x+1:]
                    if all(entry not in C for C in col_options): S=S[:x]+entry+S[x+1:]
                    if all(entry not in B for B in block_options): S=S[:x]+entry+S[x+1:]
        
        BLOCK_OPTS=[]
        for temp in range(9):
            y=max(int(temp/3)*27-9,0)
            if y==45:y=45-9
            BLOCK_OPTS.append(options[temp*3+y:(temp+1)*3+y]+options[temp*3+9+y:(temp+1)*3+9+y]+options[temp*3+18+y:(temp+1)*3+18+y])
        for x in range(9):
            block=BLOCK_OPTS[x]
            for y in range(9):
                entry=block[y]
                if len(entry)==2 and block.count(entry)==2:
                    for digit in list(entry):
                        for z in range(9):
                            if z==y: continue
                            block[z]=block[z].replace(digit,'')
                    for z in range(9):
                        if block[z]!='X' and len(block[z])==1:
                            position=(int(x/3)*3+int(z/3))*9+(z%3)+(x%3)*3
                            S=S[:position]+block[z]+S[position+1:]
    if TEMP==S: solvable=False
    return S,options,solvable

def VERIFY(S):
    status=True
    template=['1', '2', '3', '4', '5', '6', '7', '8', '9']
    ROWS,COLS,BLOK=align(S)
    for stack in [ROWS,COLS,BLOK]:
        for LIST in stack:
            if sorted(LIST)!=template: status=False
    return status

def SOLVE(S,advance=True, OPTIONS=False):
    TEMP=S
    solvable = True
    while S.count('-')>0 and solvable:
        S,options,solvable=LOGIC(S)
    if advance:
        for x in range(81):
            if len(options[x])==2:
                S1=S[:x]+options[x][0]+S[x+1:]
                S2=S[:x]+options[x][1]+S[x+1:]
                solvable=True
                while S1.count('-')>0 and solvable:
                    S1,options,solvable=LOGIC(S1)
                    if '' in options: S=S2
                solvable=True
                while S2.count('-')>0 and solvable:
                    S2,options,solvable=LOGIC(S2)
                    if '' in options: S=S1
    if TEMP==S:
        if OPTIONS:
            for x in range(9):
                if x%3==0 and x>0: print('---+---+---')
                line=options[9*x:9*x+3]+['|']+options[9*x+3:9*x+6]+['|'] +options[9*x+6:9*x+9]
                print(line)
        solvable=False
    return S,solvable


solved,unsolved,counter=0,0,0
LEN=len(sudokus)
for S in sudokus:
    counter+=1
    if len(S)!=81:
        input("Problem has %d characters" % len(S))
        continue
    solvable=True
    while S.count('-')>0 and solvable:
        S,solvable=SOLVE(S)
    if VERIFY(S):
        #PRINT(S)
        solved+=1
    else:
        S,solvable=SOLVE(S,False,False)
        if VERIFY(S):
            solved+=1
        else: unsolved+=1
    t=solved/(time()-start)
    print('\r%d+%d/%d(%d) || %f || %f'%(unsolved,solved,counter,LEN,t,1/t),end='')
    
input('\n\nSolved in %f seconds'%(time()-start))
