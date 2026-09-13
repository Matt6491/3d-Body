
"use client";
import {Canvas} from "@react-three/fiber";
import {OrbitControls} from "@react-three/drei";
import * as THREE from "three";
import {MuscleValues,MuscleKey,emptyMuscles} from "@/lib/types";

type Props={muscles?:MuscleValues;highlight?:Partial<Record<MuscleKey,"primary"|"secondary"|"stabilizer">>;compare?:boolean;current?:MuscleValues;view?:string;measurements?:any};

const roleColor={primary:"#55ffe2",secondary:"#77bdb3",stabilizer:"#385e59"};
const skin="#b98d72", suit="#202c33", seam="#30434d";

function Ellipsoid({p,s,color=suit,opacity=1}:{p:[number,number,number],s:[number,number,number],color?:string,opacity?:number}){
 return <mesh position={p} scale={s}><sphereGeometry args={[1,28,24]}/><meshStandardMaterial color={color} roughness={.62} metalness={.02} transparent opacity={opacity}/></mesh>
}
function Capsule({p,s,color=suit,rot=[0,0,0]}:{p:[number,number,number],s:[number,number,number],color?:string,rot?:[number,number,number]}){
 return <mesh position={p} scale={s} rotation={rot}><capsuleGeometry args={[.55,1.45,8,18]}/><meshStandardMaterial color={color} roughness={.66}/></mesh>
}
function Body({muscles=emptyMuscles(),highlight={},x=0,fade=1,measurements,rotation=[0,0,0]}:{muscles?:MuscleValues;highlight?:Props["highlight"];x?:number;fade?:number;measurements?:any;rotation?:[number,number,number]}){
 const m=(k:MuscleKey)=>muscles[k]||0;
 const hc=(k:MuscleKey)=>highlight?.[k]?roleColor[highlight[k]!] : undefined;
 const bulge=(k:MuscleKey,scale=.8)=>1+m(k)*scale*4.5;
 // Photo/height-derived proportions. These scale the baseline once; timeline morphs never alter them.
 const heightScale=(measurements?.height_cm||178)/178;
 const rel=(value:number|undefined,reference:number)=>(value||reference)/reference/heightScale;
 const d={
   height:heightScale,
   // Child scales are normalized by heightScale because the whole body group is already
   // scaled to supplied height. This avoids double-scaling a tall user's shoulder/limb data.
   shoulder:rel(measurements?.shoulder_width_cm,44.4),
   torso:rel(measurements?.torso_length_cm,53.4),
   chestDepth:rel(measurements?.chest_depth_cm,21.1),
   waist:rel(measurements?.waist_width_cm,29.7),
   waistDepth:rel(measurements?.waist_depth_cm,18.3),
   hip:rel(measurements?.hip_width_cm,34.1),
   arm:rel(measurements?.arm_length_cm,78.3),
   leg:rel(measurements?.leg_length_cm,94.3),
   upperArm:rel(measurements?.upper_arm_proxy_cm,29.7),
   forearm:rel(measurements?.forearm_proxy_cm,25.3),
   thigh:rel(measurements?.thigh_proxy_cm,52.4),
   calf:rel(measurements?.calf_proxy_cm,35.8),
 };
 return <group position={[x,-.2,0]} rotation={rotation} scale={[d.height,d.height,d.height]}>
   {/* head/neck */}
   <Ellipsoid p={[0,3.55,0]} s={[.46,.58,.44]} color={skin} opacity={fade}/>
   <Capsule p={[0,2.83,0]} s={[.34,.32,.34]} color={skin}/>
   {/* torso base */}
   <Ellipsoid p={[0,1.65,0]} s={[1.12*d.shoulder,1.38*d.torso,.58*d.chestDepth]} color={suit}/>
   <Ellipsoid p={[0,.72,0]} s={[.88*d.waist,.78*d.torso,.51*d.waistDepth]} color={suit}/>
   {/* chest-specific anterior lobes */}
   <Ellipsoid p={[-.48,1.88,.48]} s={[.55*bulge("pectoralisMajor",.55),.48*bulge("upperChest",.34),.18*bulge("pectoralisMajor",.9)]} color={hc("pectoralisMajor")||suit}/>
   <Ellipsoid p={[-.47,2.20,.38]} s={[.48*bulge("upperChest",.50),.25,.15*bulge("upperChest",.7)]} color={hc("upperChest")||suit}/>
   <Ellipsoid p={[.48,1.88,.48]} s={[.55*bulge("pectoralisMajor",.55),.48*bulge("upperChest",.34),.18*bulge("pectoralisMajor",.9)]} color={hc("pectoralisMajor")||suit}/>
   <Ellipsoid p={ [.47,2.20,.38]} s={[.48*bulge("upperChest",.50),.25,.15*bulge("upperChest",.7)]} color={hc("upperChest")||suit}/>
   {/* lats/back */}
   <Ellipsoid p={[0,1.55,-.46]} s={[.96*bulge("latissimus",.45),.84,.20*bulge("upperBack",.65)]} color={hc("latissimus")||hc("upperBack")||suit}/>
   {/* shoulders */}
   {([-1,1] as const).map((side)=><group key={side}>
    <Ellipsoid p={[side*1.12,2.30,.06]} s={[.50*bulge("lateralDeltoid",.7),.51*bulge("lateralDeltoid",.7),.47]} color={hc("lateralDeltoid")||hc("anteriorDeltoid")||suit}/>
    <Ellipsoid p={[side*1.08,2.34,.38]} s={[.32,.34,.18*bulge("anteriorDeltoid",1)]} color={hc("anteriorDeltoid")||suit}/>
    <Ellipsoid p={[side*1.08,2.34,-.38]} s={[.32,.34,.18*bulge("posteriorDeltoid",1)]} color={hc("posteriorDeltoid")||suit}/>
    {/* upper arm base plus directional biceps/triceps */}
    <Capsule p={[side*1.43,1.42,0]} s={[.36*d.upperArm,.73*d.arm,.36*d.upperArm]} color={skin} rot={[0,0,side*.06]}/>
    <Ellipsoid p={[side*1.43,1.55,.27]} s={[.28,.50*bulge("biceps",.58),.17*bulge("biceps",1)]} color={hc("biceps")||skin}/>
    <Ellipsoid p={[side*1.43,1.42,-.27]} s={[.29,.55*bulge("triceps",.60),.18*bulge("triceps",1)]} color={hc("triceps")||skin}/>
    <Capsule p={[side*1.55,.12,0]} s={[.28*d.forearm,.70*d.arm,.28*d.forearm*bulge("forearms",.4)]} color={hc("forearms")||skin}/>
   </group>)}
   {/* waist detail */}
   <Ellipsoid p={[0,.63,.45]} s={[.66,.61,.12*bulge("abdominals",.8)]} color={hc("abdominals")||suit}/>
   <Ellipsoid p={[-.72,.67,.18]} s={[.18*bulge("obliques",.8),.62,.28]} color={hc("obliques")||suit}/>
   <Ellipsoid p={[.72,.67,.18]} s={[.18*bulge("obliques",.8),.62,.28]} color={hc("obliques")||suit}/>
   {/* pelvis */}
   <Ellipsoid p={[0,-.05,0]} s={[.96*d.hip,.58,.60*d.waistDepth]} color={suit}/>
   <Ellipsoid p={[0,-.08,-.47]} s={[.84*bulge("glutes",.48),.50*bulge("glutes",.5),.26*bulge("glutes",1)]} color={hc("glutes")||suit}/>
   {/* legs */}
   {([-1,1] as const).map(side=><group key={"leg"+side}>
     <Capsule p={[side*.52,-1.47,0]} s={[.48*d.thigh,.93*d.leg,.48*d.thigh]} color={skin}/>
     <Ellipsoid p={[side*.52,-1.27,.36]} s={[.39,.74*bulge("quadriceps",.5),.18*bulge("quadriceps",1)]} color={hc("quadriceps")||skin}/>
     <Ellipsoid p={[side*.52,-1.38,-.34]} s={[.37,.72*bulge("hamstrings",.5),.17*bulge("hamstrings",1)]} color={hc("hamstrings")||skin}/>
     <Capsule p={[side*.52,-3.15,0]} s={[.34*d.calf,.83*d.leg,.34*d.calf]} color={skin}/>
     <Ellipsoid p={[side*.52,-3.03,-.22]} s={[.30*bulge("calves",.5),.56*bulge("calves",.5),.17*bulge("calves",1)]} color={hc("calves")||skin}/>
     <Ellipsoid p={[side*.52,-4.05,.18]} s={[.34,.18,.64]} color={skin}/>
   </group>)}
   {/* traps */}
   <Ellipsoid p={[0,2.62,-.20]} s={[.74*bulge("trapezius",.4),.34,.20*bulge("trapezius",.8)]} color={hc("trapezius")||suit}/>
 </group>
}

export default function BodyViewer({muscles=emptyMuscles(),highlight={},compare=false,current=emptyMuscles(),view="front",measurements}:Props){
 const angle=view==="back"?Math.PI:view==="left"?Math.PI/2:view==="right"?-Math.PI/2:0;
 return <div className="viewer">
  {compare&&<div className="compareLabels"><span>CURRENT</span><span>PROJECTED</span></div>}
  <Canvas camera={{position:[0,1.0,9],fov:34}}>
    <color attach="background" args={["#070b0e"]}/>
    <ambientLight intensity={1.3}/><directionalLight position={[5,6,6]} intensity={2.2}/><directionalLight position={[-4,2,-3]} intensity={1.1}/>
    {compare?<><Body muscles={current} x={-1.65} measurements={measurements} rotation={[0,angle,0]}/><Body muscles={muscles} x={1.65} highlight={highlight} measurements={measurements} rotation={[0,angle,0]}/></>:<Body muscles={muscles} highlight={highlight} measurements={measurements} rotation={[0,angle,0]}/>}
    <gridHelper args={[20,20,"#19252c","#11191e"]} position={[0,-4.30,0]}/>
    <OrbitControls enablePan={false} minDistance={6} maxDistance={14} target={[0,-.2,0]}/>
  </Canvas>
  <div className="viewer-note">Drag to rotate · scroll/pinch to zoom · same parameterized body at every checkpoint</div>
 </div>
}
