import numpy as np

def PRINT(x):
    for i in x:
        for j in i:
            print(round(j, 2), end='\t')
        print()

def p_dn(r, v, dt):
    top = np.exp(v*np.sqrt(dt/2)) - np.exp(r*dt/2) 
    bot = np.exp(v*np.sqrt(dt/2)) - np.exp(-v*np.sqrt(dt/2))
    return pow(top/bot, 2)

def p_up(r, v, dt):
    top = np.exp(r*dt/2) - np.exp(-v*np.sqrt(dt/2))
    bot = np.exp(v*np.sqrt(dt/2)) - np.exp(-v*np.sqrt(dt/2))
    return pow(top/bot, 2)

def p_m(r, v, dt):
    return 1 - (p_up(r,v,dt) + p_dn(r,v,dt))



def d(u):
    return 1/u

def u(v, dt):
    return np.exp(v*np.sqrt(2.0*dt))


def C(S, K, r, q, v, t, nodes, optype='call'):
    m, n = int(4*nodes + 2), int(nodes + 1)
    dt = t / nodes
    tree = [[0 for j in range(n)] for i in range(m)]
    split = int(m / 2 - 1)
    tree[split][0] = S

    u_ = u(v, dt)
    d_ = d(u_)

    U = p_up(r, v, dt)
    D = p_dn(r, v, dt)
    M = p_m(r, v, dt)


    ux = 2
    cs = 0

    while cs <= n:
        tree[split][cs] = S
        for i in range(cs + 1, n, 1):
            tree[split - (i - cs)*ux][i] = tree[split - (i - cs - 1)*ux][i - 1]*u_
            tree[split - (i - cs - 1)*ux][i] = tree[split - (i - cs - 1)*ux][i - 1]
            tree[split + (i - cs)*ux][i] = tree[split + (i - cs - 1)*ux][i - 1]*d_
            tree[split + (i - cs - 1)*ux][i] = tree[split + (i - cs - 1)*ux][i - 1]
        cs += 2

    for i in range(1, m, 1):
        if i % 2 != 0:
            if optype == 'put':
                tree[i][n - 1] = max(K - tree[i - 1][n - 1], 0.0)
            else:
                tree[i][n - 1] = max(tree[i - 1][n - 1] - K, 0.0)

    cx = 0
    ls = 0
    osx = 0

    for i in range(1, n, 1):
        cx = n - (i + 1)
        ls = 4 + osx
        while ls < m - osx:
            A = tree[ls - 1 - 2][cx + 1]
            B = tree[ls - 1][cx + 1]
            C = tree[ls -1 + 2][cx + 1]
            tree[ls - 1][cx] = max(np.exp(-r*dt)*(U*A + M*B + D*C), 0)
            ls += 2
        osx += 2

    return tree[split + 1][0]


def Delta(S,K,r,q,v,t,nodes,optype):
    ds = 0.01*S
    CD = C(S+ds,K,r,q,v,t,nodes,optype=optype)
    CU = C(S-ds,K,r,q,v,t,nodes,optype=optype)
    return (CD - CU)/(2*ds)

def Gamma(S,K,r,q,v,t,nodes,optype):
    dg = 0.01*S
    C1 = C(S+dg, K, r, q, v, t, nodes, optype=optype)
    CX = C(S, K, r, q, v, t, nodes, optype=optype)
    C0 = C(S-dg, K, r, q, v, t, nodes, optype=optype)
    return (C1 - 2.0*CX + C0)/pow(dg, 2)

def Theta(S,K,r,q,v,t,nodes,optype):
    dth = 1.0/365.0
    C1 = C(S,K,r,q,v,t+dth,nodes,optype=optype)
    C0 = C(S,K,r,q,v,t,nodes,optype=optype)
    return -(C1 - C0)/(2*dth)

def Vega(S,K,r,q,v,t,nodes,optype):
    dv = 0.01
    C1 = C(S,K,r,q,v+dv,t,nodes,optype=optype)
    C0 = C(S,K,r,q,v-dv,t,nodes,optype=optype)
    return ((C1 - C0)/(2*dv))/100

def Rho(S,K,r,q,v,t,nodes,optype):
    dr = 0.01
    C1 = C(S,K,r+dr,q,v,t,nodes,optype=optype)
    C0 = C(S,K,r-dr,q,v,t,nodes,optype=optype)
    return (C1 - C0)/(2*dr)

def Greeks(S,K,r,q,v,t,optype,nodes=8):
    delta = Delta(S,K,r,q,v,t,nodes,optype)
    gamma = Gamma(S,K,r,q,v,t,nodes,optype)
    theta = Theta(S,K,r,q,v,t,nodes,optype)
    vega = Vega(S,K,r,q,v,t,nodes,optype)
    rho = Rho(S,K,r,q,v,t,nodes,optype)
    if delta > 2 or delta < -2:
        delta = 0
    if gamma > 1 or gamma < -1:
        gamma = 0
    if theta > 0 or theta < -5:
        theta = 0
    if rho > 1 or rho < -1:
        rho = 0
    if optype == 'put':
        delta = -delta
    return delta, gamma, theta, vega, rho
