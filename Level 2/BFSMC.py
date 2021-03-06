import cv2
import numpy as np
import math
import queue

nP=0
m=0
n=0
S=[19,16]
G=[2,2]

q=queue.Queue()

matrix=np.zeros((25,25))

    
def box(img,p,color):
    cv2.rectangle(img,(21*p[0]+1,21*p[1]+1),(21*p[0]+20,21*p[1]+20),color,-1)

def box2(img,p,color,m):
    box(img,(p[0],m-p[1]),color)
    
def drawBackground(m,n,img):
    for i in range(n+1):
        cv2.line(img,(21*i+21,0),(21*i+21,(m+2)*21),(150,150,150),1)
        box(img,(i,0),(100,100,100))
        box(img,(i,m),(100,100,100))
    for i in range(m+1):
        cv2.line(img,(0,21*i+21),(21*(n+2),21*i+21),(150,150,150),1)
        box(img,(0,i),(100,100,100))
        box(img,(n,i),(100,100,100))

def lamtron(f):
    if (f-math.floor(f)>math.ceil(f)-f):
        return math.ceil(f)
    return math.floor(f)

def line(img,p1,p2,color):
    if (p1[0]==p2[0]):
        for i in range(min(p1[1],p2[1]),max(p1[1],p2[1])+1):
            matrix[p1[0],i]=-1
            box2(img,(p1[0],i),color,m)
        return
    if (p1[1]==p2[1]):
        for i in range(min(p1[0],p2[0]),max(p1[0],p2[0])+1):
            matrix[i,p1[1]]=-1
            box2(img,(i,p1[1]),color,m)
        return
    a=(p1[1]-p2[1])/(p1[0]-p2[0])
    b=p1[1]-a*p1[0]
    for i in range(min(p1[0],p2[0]),max(p1[0],p2[0])+1):
       box2(img,(i,lamtron(a*i+b)),color,m)
       matrix[i,lamtron(a*i+b)]=-1
    for i in range(min(p1[1],p2[1]),max(p1[1],p2[1])+1):
       box2(img,(lamtron((i-b)/a),i),color,m)
       matrix[lamtron((i-b)/a),i]=-1
def drawPolygon(P,img,color):
    for i in range(int(len(P)/2)-1):
        line(img,(P[i*2],P[i*2+1]),(P[i*2+2],P[i*2+3]),color)
    line(img,(P[len(P)-2],P[len(P)-1]),(P[0],P[1]),color)

dx=[-1,0,0,1]
dy=[0,-1,1,0]

def distance(P1,P2):
    return abs(P1[0]-P2[0])+abs(P1[1]-P2[1])

def fP(P):
    return distance(P,G)
    

def BFSMC():
    D=S
    q.put(S)
    while matrix[G[0],G[1]]==1000:
    
        for i in range(15):
            if not q.empty():
                T=q.get()
                for j in range(4):
                    if matrix[T[0]+dx[j],T[1]+dy[j]]==1000:
                        matrix[T[0]+dx[j],T[1]+dy[j]]=matrix[T[0],T[1]]+1
                        q.put([T[0]+dx[j],T[1]+dy[j]])
        valuefmin=1000
        next=[-1,-1]
        while not q.empty():
            tmp=q.get()
            if valuefmin>matrix[tmp[0],tmp[1]]+fP(tmp):
                valuefmin=matrix[tmp[0],tmp[1]]+fP(tmp)
                next=tmp
        if next!=[-1,-1]:
            q.put(next)
        else:
            
            return
    print(matrix[G[0],G[1]])
def back():
    if matrix[G[0],G[1]]==1000:
        print("khong tim thay duong di")
        return
        
    D=[G[0],G[1]]
    while matrix[D[0],D[1]]!=0:
        tmin=1000
        orient=-1
        for i in [0,1,2,3] : 
            if matrix[D[0]-dx[i],D[1]-dy[i]]!=-1 and matrix[D[0]-dx[i],D[1]-dy[i]]<=tmin:
                    tmin=matrix[D[0]-dx[i],D[1]-dy[i]]
                    orient=i
        D=[D[0]-dx[orient],D[1]-dy[orient]]
        box2(img,[D[0],D[1]],(255,255,255),m)
       

###################################################################3

f=open("input.txt","r")

m,n=list(map(int, f.readline().split()))
S[0],S[1],G[0],G[1]=list(map(int, f.readline().split()))
nP=list(map(int, f.readline().split()))[0]

img=np.zeros(((m+1)*21,(n+1)*21,3), np.uint8)

    

for i in range(25):
    for j in range(25):
        matrix[i]=1000  
drawBackground(m,n,img)

for i in range(nP):
    P=list(map(int, f.readline().split(',')))     
    drawPolygon(P,img,(255,0,0))

box2(img,S,(0,0,255),m)
box2(img,G,(0,255,0),m)




for i in range(n+2):
    matrix[i,0]=-1
    matrix[i,m+1]=-1
for i in range(m+2):
    matrix[0,i]=-1
    matrix[n+1,i]=-1


matrix[S[0],S[1]]=0

BFSMC()
back()

box2(img,S,(0,0,255),m)
cv2.imshow("no cap",img)
cv2.waitKey(0)
cv2.destroyAllWindows()