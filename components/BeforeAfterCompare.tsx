
"use client";
import {useRef,useState} from "react";
import BodyViewer from "./BodyViewer";
import {MuscleValues} from "@/lib/types";
export default function BeforeAfterCompare({current,projected,measurements,view="front"}:{current:MuscleValues;projected:MuscleValues;measurements?:any;view?:string}){
 const [split,setSplit]=useState(50); const dragging=useRef(false);
 const move=(clientX:number,el:HTMLDivElement)=>{const r=el.getBoundingClientRect();setSplit(Math.max(5,Math.min(95,((clientX-r.left)/r.width)*100)))};
 return <div style={{position:"relative",height:"100%",minHeight:560,overflow:"hidden",touchAction:"none"}}
   onPointerDown={e=>{dragging.current=true;(e.currentTarget as HTMLDivElement).setPointerCapture(e.pointerId);move(e.clientX,e.currentTarget as HTMLDivElement)}}
   onPointerMove={e=>{if(dragging.current)move(e.clientX,e.currentTarget as HTMLDivElement)}}
   onPointerUp={()=>dragging.current=false}>
   <div style={{position:"absolute",inset:0}}><BodyViewer muscles={projected} measurements={measurements} view={view}/></div>
   <div style={{position:"absolute",inset:0,clipPath:`inset(0 ${100-split}% 0 0)`}}><BodyViewer muscles={current} measurements={measurements} view={view}/></div>
   <div style={{position:"absolute",top:0,bottom:0,left:`${split}%`,width:2,background:"#7ef9e8",zIndex:8,pointerEvents:"none",boxShadow:"0 0 18px #7ef9e866"}}>
      <div style={{position:"absolute",top:"50%",left:"50%",transform:"translate(-50%,-50%)",width:30,height:44,borderRadius:999,border:"1px solid #7ef9e8",background:"#08100f",display:"grid",placeItems:"center",fontSize:12}}>↔</div>
   </div>
   <div style={{position:"absolute",top:72,left:18,zIndex:9,fontSize:10,letterSpacing:".15em"}}>CURRENT</div>
   <div style={{position:"absolute",top:72,right:18,zIndex:9,fontSize:10,letterSpacing:".15em"}}>PROJECTED</div>
   <input aria-label="Before and after divider" type="range" min="10" max="90" value={split} onChange={e=>setSplit(Number(e.target.value))}
     style={{position:"absolute",zIndex:12,left:"10%",bottom:55,width:"80%",accentColor:"#7ef9e8"}}/>
 </div>
}
