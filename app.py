
import os, math, heapq, time
from collections import deque
import streamlit as st, networkx as nx, pandas as pd, plotly.express as px, plotly.graph_objects as go, requests

st.set_page_config(page_title="GreenRoute | Municipal Intelligence",page_icon="♻️",layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}.stApp{background:#f4f8f5}
section[data-testid="stSidebar"]{background:#10382e}section[data-testid="stSidebar"] *{color:#e9f5ed!important}
.hero{background:linear-gradient(115deg,#103b30,#18734f);padding:30px 34px;border-radius:22px;color:white;margin-bottom:20px}
.hero h1{font:800 34px Manrope;color:white;margin:0 0 6px}.hero p{color:#d6eee1;margin:0}
.eyebrow{color:#a8e1c1;font-size:10px;font-weight:800;letter-spacing:2px;margin-bottom:8px}
.metric,.panel{background:white;border:1px solid #e3ede6;border-radius:16px;padding:17px;box-shadow:0 4px 14px #123b2810}
.metric small{color:#718178;font-weight:700}.metric strong{display:block;font:800 27px Manrope;color:#173e30;margin:5px 0}.metric em{font-size:11px;color:#21865b;font-style:normal}
.panel h3{font:800 17px Manrope;color:#193d30;margin:0}.panel p{font-size:12px;color:#7b8b82}
.stButton button{border-radius:10px;font-weight:700}
</style>""",unsafe_allow_html=True)

# Illustrative demo network only; not live municipal map data.
N={"Depot":(12.9716,77.5946),"Ward A":(12.978,77.602),"Ward B":(12.965,77.606),"Ward C":(12.960,77.589),"Ward D":(12.985,77.585),"Ward E":(12.990,77.610),"Ward F":(12.950,77.600),"Ward G":(12.975,77.575),"Ward H":(12.955,77.580)}
E=[("Depot","Ward A",2.2),("Depot","Ward B",3.1),("Depot","Ward C",2.8),("Depot","Ward D",3.6),("Ward A","Ward E",2.4),("Ward A","Ward D",2),("Ward B","Ward E",2.1),("Ward B","Ward F",2.7),("Ward C","Ward F",1.9),("Ward C","Ward H",2.5),("Ward D","Ward G",2),("Ward G","Ward H",2.6),("Ward E","Ward D",2.8),("Ward F","Ward H",2.2)]
G=nx.Graph()
for n,p in N.items():G.add_node(n,pos=p)
for a,b,w in E:G.add_edge(a,b,weight=w)
def cost(p):return sum(G[a][b]["weight"] for a,b in zip(p,p[1:]))
def bfs(s,g):
 q=deque([(s,[s])]);seen={s};x=0
 while q:
  n,p=q.popleft();x+=1
  if n==g:return p,x
  for v in sorted(G.neighbors(n)):
   if v not in seen:seen.add(v);q.append((v,p+[v]))
 return [],x
def dfs(s,g):
 q=[(s,[s])];seen=set();x=0
 while q:
  n,p=q.pop()
  if n in seen:continue
  seen.add(n);x+=1
  if n==g:return p,x
  for v in sorted(G.neighbors(n),reverse=True):
   if v not in seen:q.append((v,p+[v]))
 return [],x
def ucs(s,g,astar=False,greedy=False):
 def h(a):
  y1,x1=N[a];y2,x2=N[g];return math.hypot(y1-y2,x1-x2)*111
 q=[(h(s) if greedy else 0,s,[s],0)];best={s:0};x=0
 while q:
  _,n,p,c=q.pop(0) if False else heapq.heappop(q);x+=1
  if n==g:return p,x
  for v in G.neighbors(n):
   nc=c+G[n][v]["weight"]
   if nc<best.get(v,1e9):
    best[v]=nc;priority=h(v) if greedy else nc+(h(v)*.55 if astar else 0)
    heapq.heappush(q,(priority,v,p+[v],nc))
 return [],x
def mapfig(path=[]):
 f=go.Figure()
 for a,b,w in E:
  f.add_trace(go.Scattermap(lat=[N[a][0],N[b][0]],lon=[N[a][1],N[b][1]],mode="lines",line=dict(width=3,color="#cbd8d0"),showlegend=False,hoverinfo="skip"))
 if path:
  f.add_trace(go.Scattermap(lat=[N[x][0] for x in path],lon=[N[x][1] for x in path],mode="lines+markers+text",text=path,textposition="top right",line=dict(width=6,color="#159866"),marker=dict(size=10,color="#0d6b49"),showlegend=False))
 f.update_layout(map=dict(style="open-street-map",center=dict(lat=12.971,lon=77.595),zoom=11),height=390,margin=dict(l=0,r=0,t=0,b=0))
 return f
wards=pd.DataFrame([["Ward A",82,1.8,True],["Ward B",96,2.4,True],["Ward C",61,1.5,False],["Ward D",45,1.2,False],["Ward E",91,2.1,True],["Ward F",74,1.7,False],["Ward G",38,.9,False],["Ward H",88,2,True]],columns=["Ward","Bin fill %","Waste (tonnes)","Priority"])
def ai(messages):
 key=os.getenv("GROQ_API_KEY","")
 if not key:return "Demo mode: add your private GROQ_API_KEY in hosting secrets to enable live AI responses."
 data={"model":os.getenv("GROQ_MODEL","openai/gpt-oss-20b"),"temperature":.2,"messages":[{"role":"system","content":"You are GreenRoute's helpful citizen waste-management assistant. Give practical, concise guidance about waste segregation, collection preparation and responsible disposal. Never invent local schedules, official contacts or claim to submit complaints. Direct users to their municipal authority for local official information."}]+messages}
 try:
  r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":"Bearer "+key},json=data,timeout=45);r.raise_for_status();return r.json()["choices"][0]["message"]["content"]
 except Exception as e:return "AI connection error. Check the Groq key and model setting. "+str(e)

st.sidebar.markdown("## ♻️ GreenRoute")
st.sidebar.caption("MUNICIPAL INTELLIGENCE PLATFORM")
page=st.sidebar.radio("WORKSPACE",["Overview","Smart Route Planner","Ward Assignment","Citizen AI Assistant","Operations & Analytics"])
st.sidebar.markdown("---")
st.sidebar.success("Demo network online")
st.sidebar.caption("Sample data • Not connected to live municipal systems")
def hero(k,t,s):st.markdown(f'<div class="hero"><div class="eyebrow">{k}</div><h1>{t}</h1><p>{s}</p></div>',unsafe_allow_html=True)
def metric(k,v,n):st.markdown(f'<div class="metric"><small>{k}</small><strong>{v}</strong><em>{n}</em></div>',unsafe_allow_html=True)

if page=="Overview":
 hero("SMART WASTE COLLECTION • CONTROL CENTER","A cleaner city starts with a smarter route.","Coordinate collection, prioritise overflowing bins and make better fleet decisions.")
 cols=st.columns(4)
 for c,args in zip(cols,[("ACTIVE WARDS","8","Demo network"),("FLEET CAPACITY","24 t","Illustrative capacity"),("PRIORITY ALERTS","4","Wards above 80% fill"),("ROAD LINKS","14","Simulated connections")]):
  with c:metric(*args)
 l,r=st.columns([1.4,1])
 with l:
  st.markdown('<div class="panel"><h3>Collection network</h3><p>Illustrative ward connections around the depot</p></div>',unsafe_allow_html=True);st.plotly_chart(mapfig(),use_container_width=True)
 with r:
  st.markdown('<div class="panel"><h3>Priority wards</h3><p>Bins with fill level at or above 80%</p></div>',unsafe_allow_html=True)
  for _,x in wards[wards.Priority].iterrows():st.warning(f'{x.Ward}  ·  {x["Bin fill %"]}% full')
 st.info("All ward coordinates, road links and figures are sample data for demonstration, not verified municipal or live traffic data.")

elif page=="Smart Route Planner":
 hero("OPTIMISATION ENGINE","Smart Route Planner","Compare classic AI search strategies and find a low-cost route through the demo network.")
 a,b,c=st.columns(3)
 with a:s=st.selectbox("Starting point",list(N))
 with b:g=st.selectbox("Destination",list(N),index=4)
 with c:alg=st.selectbox("Search strategy",["A* Search","Uniform Cost Search","Breadth-First Search","Depth-First Search","Greedy Best-First"])
 if st.button("✨ Calculate route",type="primary",use_container_width=True):
  fn={"A* Search":lambda:ucs(s,g,astar=True),"Uniform Cost Search":lambda:ucs(s,g),"Breadth-First Search":lambda:bfs(s,g),"Depth-First Search":lambda:dfs(s,g),"Greedy Best-First":lambda:ucs(s,g,greedy=True)}[alg]
  t=time.perf_counter();p,x=fn();ms=(time.perf_counter()-t)*1000;st.session_state.route=(p,x,ms,alg)
 if "route" in st.session_state:
  p,x,ms,alg=st.session_state.route
  a,b,c=st.columns(3)
  with a:metric("ROUTE COST",f"{cost(p):.1f} km","Demo edge weights")
  with b:metric("NODES EXPANDED",x,"Search effort")
  with c:metric("COMPUTE TIME",f"{ms:.3f} ms","Local simulation")
  st.plotly_chart(mapfig(p),use_container_width=True);st.success(" → ".join(p) if p else "No route found.")
 st.caption("This demonstrates graph-search methods; it is not live vehicle navigation or traffic-aware routing.")
 if st.button("Compare all algorithms"):
  rows=[]
  for name,fn in [("BFS",lambda:bfs(s,g)),("DFS",lambda:dfs(s,g)),("UCS",lambda:ucs(s,g)),("Greedy",lambda:ucs(s,g,greedy=True)),("A*",lambda:ucs(s,g,astar=True))]:
   t=time.perf_counter();p,x=fn();rows.append({"Algorithm":name,"Path cost (km)":round(cost(p),2),"Nodes expanded":x,"Time (ms)":round((time.perf_counter()-t)*1000,4),"Path":" → ".join(p)})
  st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

elif page=="Ward Assignment":
 hero("FLEET COORDINATION","Ward Assignment","Allocate collection work to trucks while respecting carrying capacity.")
 cap=st.slider("Capacity per truck (tonnes)",3.,12.,6.,.5);trucks=st.slider("Available trucks",1,8,4)
 edited=st.data_editor(wards[["Ward","Waste (tonnes)","Bin fill %","Priority"]],use_container_width=True,hide_index=True)
 if st.button("⚙️ Assign wards to trucks",type="primary",use_container_width=True):
  bins=[[] for _ in range(trucks)];loads=[0.]*trucks;un=[]
  for j in edited.sort_values(["Priority","Bin fill %","Waste (tonnes)"],ascending=False).to_dict("records"):
   ix=sorted(range(trucks),key=lambda z:loads[z]);placed=False
   for i in ix:
    if loads[i]+float(j["Waste (tonnes)"])<=cap:bins[i].append(j);loads[i]+=float(j["Waste (tonnes)"]);placed=True;break
   if not placed:un.append(j["Ward"])
  st.session_state.alloc=(bins,loads,un)
 if "alloc" in st.session_state:
  bins,loads,un=st.session_state.alloc;cols=st.columns(min(trucks,4))
  for i,(jobs,load) in enumerate(zip(bins,loads)):
   with cols[i%len(cols)]:
    st.markdown(f'<div class="panel"><h3>Truck {i+1:02}</h3><strong style="font-size:25px;color:#176c4b">{load:.1f} t</strong><p>of {cap:.1f} t capacity</p><b>Assigned wards</b><br>{"<br>".join(j["Ward"] for j in jobs) or "None"}</div>',unsafe_allow_html=True)
  st.warning("Unassigned: "+", ".join(un)) if un else st.success("All wards assigned within capacity.")
 st.caption("Priority-first greedy allocation demonstration, not a guaranteed optimal CSP solver.")

elif page=="Citizen AI Assistant":
 hero("PUBLIC INFORMATION DESK","Citizen AI Assistant","Ask about waste segregation, collection preparation and responsible disposal.")
 if "chat" not in st.session_state:st.session_state.chat=[]
 for m in st.session_state.chat:
  with st.chat_message(m["role"]):st.markdown(m["content"])
 prompt=st.chat_input("How should I separate wet and dry waste?")
 if prompt:
  st.session_state.chat.append({"role":"user","content":prompt})
  with st.chat_message("user"):st.markdown(prompt)
  with st.chat_message("assistant"):
   with st.spinner("GreenRoute is thinking..."):answer=ai(st.session_state.chat[-12:])
   st.markdown(answer)
  st.session_state.chat.append({"role":"assistant","content":answer})
 if st.button("Clear conversation"):st.session_state.chat=[];st.rerun()
 if not os.getenv("GROQ_API_KEY"):st.info("Live AI is not enabled yet. Add GROQ_API_KEY to your app's private secrets.")

elif page=="Operations & Analytics":
 hero("PERFORMANCE INTELLIGENCE","Operations & Analytics","Understand collection demand, monitor priorities and evaluate the demo fleet.")
 a,b,c=st.columns(3)
 with a:metric("TOTAL WASTE",f'{wards["Waste (tonnes)"].sum():.1f} t',"Sample daily demand")
 with b:metric("AVERAGE BIN FILL",f'{wards["Bin fill %"].mean():.0f}%',"Across demo wards")
 with c:metric("PRIORITY WARDS",str(int(wards.Priority.sum())),"Needs attention")
 l,r=st.columns(2)
 with l:st.plotly_chart(px.bar(wards.sort_values("Bin fill %",ascending=False),x="Ward",y="Bin fill %",color="Priority",color_discrete_map={True:"#e49a45",False:"#23966b"},title="Bin fill level by ward"),use_container_width=True)
 with r:st.plotly_chart(px.pie(wards,names="Ward",values="Waste (tonnes)",hole=.6,title="Waste demand distribution"),use_container_width=True)
 st.dataframe(wards,use_container_width=True,hide_index=True)
 st.download_button("⬇️ Download sample data",wards.to_csv(index=False).encode(),file_name="greenroute_sample_wards.csv",mime="text/csv")

st.markdown("---")
st.markdown("<center><small style='color:#87968d'>GREENROUTE • MUNICIPAL WASTE TRUCK ROUTING AGENTS • EDUCATIONAL PROTOTYPE</small></center>",unsafe_allow_html=True)
