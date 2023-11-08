import numpy as np
import asyncio

nodes = 40
treez = []
for i in range(nodes+1):
    treez += [0 for k in range(4*i+2)]

def p_dn(r, q, v, dt):
    top = np.exp(v*np.sqrt(dt/2)) - np.exp((r - q)*dt/2) 
    bot = np.exp(v*np.sqrt(dt/2)) - np.exp(-v*np.sqrt(dt/2))
    return pow(top/bot, 2) if bot != 0 else 0

def p_up(r, q, v, dt):
    top = np.exp((r - q)*dt/2) - np.exp(-v*np.sqrt(dt/2))
    bot = np.exp(v*np.sqrt(dt/2)) - np.exp(-v*np.sqrt(dt/2))
    return pow(top/bot, 2) if bot != 0 else 0

def p_m(r, q, v, dt):
    return 1 - (p_up(r,q,v,dt) + p_dn(r,q,v,dt))

def d(u):
    return 1/u

def u(v, dt):
    return np.exp(v*np.sqrt(2.0*dt))


def C(treex, S, K, r, q, v, t, nodes, optype):
    dt = t / nodes
    
    tree_n = len(treex)
    U = u(v, dt)
    D = d(U)

    PU = p_up(r, q, v, dt)
    PD = p_dn(r, q, v, dt)
    PS = p_m(r, q, v, dt)

    cutoff = 1
    e = 0
    for p in range(nodes+1):
        f = p
        for j in range(cutoff):
            treex[e] = S*U**f
            f -= 1
            e += 2
        cutoff += 2


    head = tree_n - 4*nodes - 2
    for i in range(head, tree_n):
        if i % 2 != 0:
            if optype == 'call':
                treex[i] = np.max([treex[i-1] - K, 0])
            else:
                treex[i] = np.max([K - treex[i-1], 0])
            
    for node in range(nodes, 0, -1):
        bread = head - 4*(node - 1) - 2
        ix = 0
        for qp in range(bread, head):
            if qp % 2 != 0:
                cost = np.exp(-r*dt)*(PU*treex[head+1+ix] + PS*treex[head+3+ix] + PD*treex[head+5+ix])
                if optype == 'call':
                    treex[qp] = np.max([cost, treex[qp-1] - K])
                else:
                    treex[qp] = np.max([cost, K - treex[qp-1]])
                ix += 2
        
        head = head - 4*(node - 1) - 2
        
    
    return treex[1]


async def Delta(tree,S,K,r,q,v,t,nodes,optype):
    ds = 0.01*S
    CD = C(tree,S+ds,K,r,q,v,t,nodes,optype)
    CU = C(tree,S-ds,K,r,q,v,t,nodes,optype)
    delta = (CD - CU)/(2*ds)
    if delta > 1 or delta < -1:
        delta = 0
    return delta

async def Gamma(tree,S,K,r,q,v,t,nodes,optype):
    dg = 0.01*S
    C1 = C(tree,S+dg, K, r, q, v, t, nodes, optype)
    CX = C(tree,S, K, r, q, v, t, nodes, optype)
    C0 = C(tree,S-dg, K, r, q, v, t, nodes, optype)
    gamma = (C1 - 2.0*CX + C0)/pow(dg, 2)
    if gamma > 1 or gamma < -1:
        gamma = 0
    return gamma

async def Theta(tree,S,K,r,q,v,t,nodes,optype):
    dth = 1.0/365.0
    C1 = C(tree,S,K,r,q,v,t+dth,nodes,optype)
    C0 = C(tree,S,K,r,q,v,t,nodes,optype)
    theta = -(C1 - C0)/dth
    if theta < -10 or theta > 0:
        theta = 0
    return theta

async def Vega(tree,S,K,r,q,v,t,nodes,optype):
    dv = 0.01
    C1 = C(tree,S,K,r,q,v+dv,t,nodes,optype)
    C0 = C(tree,S,K,r,q,v-dv,t,nodes,optype)
    vega = ((C1 - C0)/(2*dv))/100
    if vega > 5 or vega < 0:
        vega = 0
    return vega

async def Rho(tree,S,K,r,q,v,t,nodes,optype):
    dr = 0.01
    C1 = C(tree,S,K,r+dr,q,v,t,nodes,optype)
    C0 = C(tree,S,K,r-dr,q,v,t,nodes,optype)
    rho = ((C1 - C0)/(2*dr))/100
    if rho < -2 or rho > 2:
        rho = 0
    return rho

async def Greeks(S,K,r,q,v,t,optype,nodes):
    tasks = []
    for func in (Delta, Gamma, Theta, Vega, Rho):
        tasks.append(asyncio.ensure_future(func(treez,S,K,r,q,v,t,nodes,optype)))
    result = await asyncio.wait(tasks)
    results = {name:0 for name in ('Delta','Gamma','Theta','Vega','Rho')}
    for r in result[0]:
        label = str(r._coro).split(' ')[2]
        results[label] = r._result
    return results['Delta'], results['Gamma'], results['Theta'], results['Vega'], results['Rho']



