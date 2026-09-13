
"use client";
import {useEffect,useMemo,useState} from "react";
import BodyViewer from "@/components/BodyViewer";
import BeforeAfterCompare from "@/components/BeforeAfterCompare";
import seedExercises from "@/data/exercises.json";
import {analyzeBody,deleteBody,deleteAnalysis,simulateTimeline,interpolateTimeline,TimelineState} from "@/lib/api";
import {Exercise,MuscleKey,MuscleValues,emptyMuscles,labels,MUSCLES} from "@/lib/types";

type Tab="body"|"train"|"future"|"map";
type RoutineItem={exercise_id:string;sets:number;reps:number;days_per_week:number;rir:number;load_factor?:number;reps_per_session?:number;resistance_kg?:number};
const checkpoints=[0,2,4,8,12,26,39,52];
const checkpointLabel=(w:number)=>w===0?"START":w<12?`${w}W`:w===12?"12W":w===26?"6M":w===39?"9M":"12M";
const prettyWeeks=(w:number)=>w===0?"Start":w<12?`${w} weeks`:w===12?"12 weeks":w===26?"6 months":w===39?"9 months":w===52?"12 months":`${w} weeks`;

export default function Home(){
 const exercises=seedExercises as Exercise[];
 const [tab,setTab]=useState<Tab>("body");
 const [age,setAge]=useState(35),[sex,setSex]=useState("male"),[height,setHeight]=useState(178),[weight,setWeight]=useState(80),[experience,setExperience]=useState("intermediate"),[maxPushups,setMaxPushups]=useState(25);
 const [bodyFatEstimate,setBodyFatEstimate]=useState(""),[trainingFrequency,setTrainingFrequency]=useState(""),[resistanceKg,setResistanceKg]=useState("");
 const [knownShoulder,setKnownShoulder]=useState(""),[knownWaist,setKnownWaist]=useState(""),[knownHip,setKnownHip]=useState("");
 const [adult,setAdult]=useState(false),[consent,setConsent]=useState(false),[autoDelete,setAutoDelete]=useState(true),[excludeFace,setExcludeFace]=useState(true);
 const [photos,setPhotos]=useState<Record<string,File|undefined>>({}); const [bodyId,setBodyId]=useState<string>(); const [analysisId,setAnalysisId]=useState<string>();
 const [measurements,setMeasurements]=useState<any>(); const [busy,setBusy]=useState(false); const [error,setError]=useState("");
 const [selected,setSelected]=useState("pushup"); const [mode,setMode]=useState<"simple"|"structured">("simple");
 const [reps,setReps]=useState(100),[days,setDays]=useState(7),[sets,setSets]=useState(5),[rir,setRir]=useState(2);
 const [recovery,setRecovery]=useState(85),[adherence,setAdherence]=useState(90);
 const [weeks,setWeeks]=useState(12); const [muscles,setMuscles]=useState<MuscleValues>(emptyMuscles());
 const [timeline,setTimeline]=useState<TimelineState[]>([]); const [routine,setRoutine]=useState<RoutineItem[]>([]);
 const [view,setView]=useState("front"),[compareMode,setCompareMode]=useState<"single"|"side"|"divider">("single"); const [mapExercise,setMapExercise]=useState("pushup");
 const [reverseMuscle,setReverseMuscle]=useState<MuscleKey>("pectoralisMajor"); const [simBusy,setSimBusy]=useState(false);

 const ex=exercises.find(e=>e.id===selected)!; const mapEx=exercises.find(e=>e.id===mapExercise)!;
 const highlight=useMemo(()=>{const h:Partial<Record<MuscleKey,"primary"|"secondary"|"stabilizer">>={};mapEx.primaryMuscles.forEach(m=>h[m]="primary");mapEx.secondaryMuscles.forEach(m=>h[m]="secondary");mapEx.stabilizers.forEach(m=>h[m]="stabilizer");return h},[mapEx]);
 const reverseExercises=useMemo(()=>exercises.filter(e=>e.primaryMuscles.includes(reverseMuscle)||e.secondaryMuscles.includes(reverseMuscle)),[reverseMuscle,exercises]);

 async function reconstruct(){
   setError(""); if(!adult||!consent){setError("Confirm adult eligibility and photo-processing consent.");return}
   if(!photos.front||!photos.side||!photos.back){setError("Front, side, and back photographs are required.");return}
   const fd=new FormData(); fd.append("front",photos.front);fd.append("side",photos.side);fd.append("back",photos.back);
   Object.entries({age:String(age),sex,height_cm:String(height),weight_kg:String(weight),experience,consent:"true",adult_confirmed:"true",auto_delete_originals:String(autoDelete),exclude_face:String(excludeFace)}).forEach(([k,v])=>fd.append(k,v));
   if(bodyFatEstimate)fd.append("body_fat_estimate",bodyFatEstimate); if(trainingFrequency)fd.append("training_frequency",trainingFrequency);
   if(knownShoulder)fd.append("known_shoulder_width_cm",knownShoulder); if(knownWaist)fd.append("known_waist_width_cm",knownWaist); if(knownHip)fd.append("known_hip_width_cm",knownHip);
   setBusy(true);try{const r=await analyzeBody(fd);setBodyId(r.bodyId);setAnalysisId(r.analysisId);setMeasurements(r.body.measurements);setTab("body")}catch(e:any){setError(e.message)}finally{setBusy(false)}
 }
 function draftItem():RoutineItem{
   if(mode==="simple"){
     const perSet=Math.max(1,Math.min(reps,maxPushups||20));
     return {exercise_id:selected,sets:Math.max(1,Math.ceil(reps/perSet)),reps:perSet,days_per_week:days,rir:2,reps_per_session:reps};
   }
   return {exercise_id:selected,sets,reps:Math.max(1,Math.round(reps/Math.max(sets,1))),days_per_week:days,rir,...(resistanceKg?{resistance_kg:Number(resistanceKg)}:{})};
 }
 function activeWorkout():RoutineItem[]{return mode==="structured"&&routine.length?routine:[draftItem()]}
 function addRoutineItem(){
   const item=draftItem();
   setRoutine(r=>[...r,item]);
 }
 async function refreshTimeline(initialWeeks=weeks){
   if(!bodyId){setError("Create a baseline body before simulating training.");return}
   setSimBusy(true);setError("");
   try{
     const states=await simulateTimeline(activeWorkout(),{age,sex,experience,maxPushups,recovery:recovery/100,adherence:adherence/100});
     setTimeline(states);setWeeks(initialWeeks);setMuscles(interpolateTimeline(states,initialWeeks));
   }catch(e:any){setError(e.message || "Simulation failed")}finally{setSimBusy(false)}
 }
 function moveTimeline(w:number){
   setWeeks(w);
   if(timeline.length)setMuscles(interpolateTimeline(timeline,w));
 }
 useEffect(()=>{if(tab==="future"&&!timeline.length&&bodyId)refreshTimeline(weeks)},[tab]); // eslint-disable-line react-hooks/exhaustive-deps

 function loadQA(){
  setAdult(true);setConsent(true);setAge(35);setSex("male");setHeight(178);setWeight(80);setExperience("intermediate");setMaxPushups(25);setSelected("pushup");setReps(100);setDays(7);
  setMeasurements({height_cm:178,weight_kg:80,shoulder_width_cm:44.2,torso_length_cm:53.4,chest_depth_cm:21.6,waist_width_cm:31,waist_depth_cm:19.2,hip_width_cm:35});
  setBodyId("qa-local-profile"); setRoutine([]); setTimeline([]); setTab("train");
 }
 async function wipe(){
   if(bodyId&&bodyId!=="qa-local-profile")try{await deleteBody(bodyId)}catch{}
   if(analysisId)try{await deleteAnalysis(analysisId)}catch{}
   setBodyId(undefined);setAnalysisId(undefined);setMeasurements(undefined);setMuscles(emptyMuscles());setTimeline([]);setRoutine([]);setPhotos({});setTab("body");
 }

 return <main className="shell">
  <header className="topbar">
   <div className="brand">FORM</div>
   <nav className="nav">{([["body","MY BODY"],["train","TRAIN"],["future","FUTURE"],["map","MUSCLE MAP"]] as const).map(([k,v])=><button key={k} className={tab===k?"active":""} onClick={()=>setTab(k)}>{v}</button>)}</nav>
   <div className="status">● TRAINING-ONLY MODEL</div>
  </header>
  <section className="workspace">
   <aside className="panel">
    {tab==="body"&&<>
      <div className="eyebrow">Personal reconstruction</div><h1 className="title">{bodyId?"Your baseline body":"Build your baseline"}</h1>
      <p className="muted">Three clothed full-body photos plus height provide a consistent geometry baseline. Estimates are not medical measurements.</p>
      {!bodyId?<>
       <div className="card"><h3>1 · Adult profile</h3>
        <div className="row"><div className="field"><label>Age</label><input type="number" min={18} value={age} onChange={e=>setAge(+e.target.value)}/></div><div className="field"><label>Biological sex</label><select value={sex} onChange={e=>setSex(e.target.value)}><option value="male">Male</option><option value="female">Female</option></select></div></div>
        <div className="row"><div className="field"><label>Height · cm</label><input type="number" value={height} onChange={e=>setHeight(+e.target.value)}/></div><div className="field"><label>Weight · kg</label><input type="number" value={weight} onChange={e=>setWeight(+e.target.value)}/></div></div>
        <div className="field"><label>Training experience</label><select value={experience} onChange={e=>setExperience(e.target.value)}><option>beginner</option><option>intermediate</option><option>advanced</option></select></div>
        <div className="field"><label>Max good-form pushups · optional</label><input type="number" value={maxPushups} onChange={e=>setMaxPushups(+e.target.value)}/></div><div className="row"><div className="field"><label>Body fat % · optional</label><input type="number" placeholder="Self estimate" value={bodyFatEstimate} onChange={e=>setBodyFatEstimate(e.target.value)}/></div><div className="field"><label>Training sessions/week · optional</label><input type="number" placeholder="0–14" value={trainingFrequency} onChange={e=>setTrainingFrequency(e.target.value)}/></div></div><div className="field"><label>Known widths · cm · optional overrides</label><div className="row"><input aria-label="Known shoulder width" type="number" placeholder="Shoulder" value={knownShoulder} onChange={e=>setKnownShoulder(e.target.value)}/><input aria-label="Known waist width" type="number" placeholder="Waist" value={knownWaist} onChange={e=>setKnownWaist(e.target.value)}/></div><input style={{marginTop:6}} aria-label="Known hip width" type="number" placeholder="Hip width" value={knownHip} onChange={e=>setKnownHip(e.target.value)}/></div>
        <label className="check"><input type="checkbox" checked={adult} onChange={e=>setAdult(e.target.checked)}/><span>I confirm I am 18 or older and these are photos of my own adult body.</span></label>
       </div>
       <div className="card"><h3>2 · Photos</h3><p className="muted">Wear fitted athletic clothing. Nudity is not required. Face may be cropped before upload.</p>
        <div className="uploads">{(["front","side","back"] as const).map(k=><label className={`upload ${photos[k]?"has":""}`} key={k}><input hidden type="file" accept="image/*" onChange={e=>setPhotos(p=>({...p,[k]:e.target.files?.[0]}))}/>{photos[k]?"✓ ":"＋ "}{k.toUpperCase()}</label>)}</div>
        <label className="check"><input type="checkbox" checked={consent} onChange={e=>setConsent(e.target.checked)}/><span>I consent to local/body-analysis processing. Photos are not used for model training.</span></label>
        <label className="check"><input type="checkbox" checked={autoDelete} onChange={e=>setAutoDelete(e.target.checked)}/><span>Delete original photos automatically after reconstruction.</span></label><label className="check"><input type="checkbox" checked={excludeFace} onChange={e=>setExcludeFace(e.target.checked)}/><span>Exclude face appearance from the body model. Head position may still be used as a geometric landmark.</span></label>
        <button className="primary" disabled={busy} onClick={reconstruct}>{busy?"ANALYZING…":"CREATE BODY"}</button>
        <button className="ghost" style={{width:"100%",marginTop:8}} onClick={loadQA}>LOAD 35M PUSHUP QA PROFILE</button>
       </div>
      </>:<><div className="card"><h3>Estimated proportions</h3>{measurements&&Object.entries(measurements).filter(([k])=>k.endsWith("_cm")).slice(0,8).map(([k,v])=><div className="metric" key={k}><span>{k.replaceAll("_"," ")}</span><span>{String(v)} cm</span></div>)}</div>
       <div className="notice">Your baseline geometry is held stable through the timeline. Muscle parameters deform local regions; body-fat mode remains CONSTANT.</div>
      </>}
    </>}
    {tab==="train"&&<>
      <div className="eyebrow">Training stimulus</div><h1 className="title">Choose the work.</h1><p className="muted">Exercise selection controls anatomical stimulus. No generic “more muscular” transform exists.</p>
      <div className="tabs"><button className={mode==="simple"?"active":""} onClick={()=>setMode("simple")}>SIMPLE</button><button className={mode==="structured"?"active":""} onClick={()=>setMode("structured")}>STRUCTURED</button></div>
      <div className="card"><div className="field"><label>Exercise</label><select value={selected} onChange={e=>setSelected(e.target.value)}>{exercises.map(e=><option key={e.id} value={e.id}>{e.name}</option>)}</select></div>
       {mode==="simple"?<><div className="field"><label>Repetitions / session</label><input type="number" value={reps} onChange={e=>setReps(+e.target.value)}/></div><div className="field"><label>Days / week</label><input type="number" min={1} max={7} value={days} onChange={e=>setDays(+e.target.value)}/></div></>:<>
       <div className="row"><div className="field"><label>Sets</label><input type="number" value={sets} onChange={e=>setSets(+e.target.value)}/></div><div className="field"><label>Total reps</label><input type="number" value={reps} onChange={e=>setReps(+e.target.value)}/></div></div><div className="row"><div className="field"><label>Days/week</label><input type="number" value={days} onChange={e=>setDays(+e.target.value)}/></div><div className="field"><label>Reps in reserve</label><input type="number" value={rir} onChange={e=>setRir(+e.target.value)}/></div></div>
       <div className="field"><label>External resistance · kg · optional</label><input type="number" placeholder="Recorded; RIR estimates relative effort" value={resistanceKg} onChange={e=>setResistanceKg(e.target.value)}/></div></>}
       {ex.loadType==="bodyweight"&&<div className="field"><label>Max consecutive good-form pushups</label><input type="number" value={maxPushups} onChange={e=>setMaxPushups(+e.target.value)}/></div>}
       {mode==="structured"&&<button className="ghost" style={{width:"100%",marginBottom:8}} onClick={addRoutineItem}>＋ ADD EXERCISE TO ROUTINE</button>}
       <button className="primary" disabled={!bodyId||simBusy} onClick={()=>{setTab("future");refreshTimeline(12)}}>{simBusy?"CALCULATING…":"SIMULATE ROUTINE"}</button>
      </div>
      <div className="card"><h3>Simulation assumptions</h3><div className="row"><div className="field"><label>Recovery · {recovery}%</label><input type="range" min="40" max="100" value={recovery} onChange={e=>setRecovery(+e.target.value)}/></div><div className="field"><label>Adherence · {adherence}%</label><input type="range" min="40" max="100" value={adherence} onChange={e=>setAdherence(+e.target.value)}/></div></div><p className="muted">These modify modeled response, not body fat. Actual sleep, nutrition, technique and recovery remain uncertain.</p></div>
       {mode==="structured"&&routine.length>0&&<div className="card"><h3>Routine · {routine.length} exercise{routine.length>1?"s":""}</h3>
        {routine.map((r,i)=>{const re=exercises.find(e=>e.id===r.exercise_id);return <div className="exercise" key={`${r.exercise_id}-${i}`}><div><b>{re?.name}</b><small>{r.sets} sets · {r.reps} reps/set · {r.days_per_week}d/w · RIR {r.rir}{r.resistance_kg!==undefined?` · ${r.resistance_kg}kg`:""}</small></div><button className="ghost danger" onClick={()=>setRoutine(xs=>xs.filter((_,j)=>j!==i))}>REMOVE</button></div>})}
       </div>}
       <div className="card"><h3>{ex.name} · anatomical roles</h3>{ex.primaryMuscles.map(m=><div className="metric" key={m}><span>{labels[m]}</span><span className="role primary">Primary</span></div>)}{ex.secondaryMuscles.map(m=><div className="metric" key={m}><span>{labels[m]}</span><span className="role secondary">Secondary</span></div>)}{ex.stabilizers.map(m=><div className="metric" key={m}><span>{labels[m]}</span><span className="role stabilizer">Stabilizer</span></div>)}</div>
    </>}
    {tab==="future"&&<>
      <div className="eyebrow">Possible visual progression</div><h1 className="title">Estimated adaptation.</h1><p className="muted">Deterministic training-only model with diminishing returns, recovery limits, repeated-bout adaptation, and experience-level response.</p>
      <div className="tabs"><button className={compareMode==="single"?"active":""} onClick={()=>setCompareMode("single")}>PROJECTED</button><button className={compareMode==="side"?"active":""} onClick={()=>setCompareMode("side")}>SIDE × SIDE</button><button className={compareMode==="divider"?"active":""} onClick={()=>setCompareMode("divider")}>DIVIDER</button></div>
      <div className="card"><h3>Largest projected parameters</h3>{Object.entries(muscles).sort((a,b)=>b[1]-a[1]).slice(0,6).map(([m,v])=><div className="metric" key={m}><span>{labels[m as MuscleKey]}</span><span className="delta">+{(v*100).toFixed(1)} normalized</span></div>)}</div>
      <div className="notice">This simulation isolates estimated training adaptation and does not assume dietary changes or automatic fat loss.</div>
    </>}
    {tab==="map"&&<>
     <div className="eyebrow">Anatomical explorer</div><h1 className="title">Muscle map.</h1><div className="field"><label>Exercise</label><select value={mapExercise} onChange={e=>setMapExercise(e.target.value)}>{exercises.map(e=><option key={e.id} value={e.id}>{e.name}</option>)}</select></div>
     <div className="card"><h3>{mapEx.name}</h3>{mapEx.primaryMuscles.map(m=><div className="metric" key={m}><span>{labels[m]}</span><span className="role primary">Primary</span></div>)}{mapEx.secondaryMuscles.map(m=><div className="metric" key={m}><span>{labels[m]}</span><span className="role secondary">Secondary</span></div>)}{mapEx.stabilizers.map(m=><div className="metric" key={m}><span>{labels[m]}</span><span className="role stabilizer">Support</span></div>)}</div>
     <div className="field"><label>Reverse lookup · tap a muscle</label>
       <div className="muscle-list">{MUSCLES.map(m=><button key={m} className={`muscle-btn ${reverseMuscle===m?"active":""}`} onClick={()=>setReverseMuscle(m)}>{labels[m]}</button>)}</div>
     </div>
     <div className="card"><h3>Exercises training {labels[reverseMuscle]}</h3>{reverseExercises.slice(0,8).map(e=><div className="exercise" key={e.id}><div><b>{e.name}</b><small>{e.movementPattern}</small></div><span className={`role ${e.primaryMuscles.includes(reverseMuscle)?"primary":"secondary"}`}>{e.primaryMuscles.includes(reverseMuscle)?"Primary":"Secondary"}</span></div>)}</div>
    </>}
    {error&&<div className="notice" style={{borderColor:"#ff7585",color:"#ffb2bb"}}>{error}</div>}
   </aside>

   <section style={{position:"relative",minWidth:0}}>
    <div className="viewer-overlay">{["front","back","left","right"].map(v=><button className={view===v?"active":""} key={v} onClick={()=>setView(v)}>{v.toUpperCase()}</button>)}</div>
    {tab==="map"?<BodyViewer muscles={emptyMuscles()} highlight={highlight} view={view} measurements={measurements}/>:tab==="future"&&compareMode==="divider"?<BeforeAfterCompare current={emptyMuscles()} projected={muscles} measurements={measurements} view={view}/>:<BodyViewer muscles={tab==="future"?muscles:emptyMuscles()} current={emptyMuscles()} compare={tab==="future"&&compareMode==="side"} view={view} measurements={measurements}/>}
   </section>

   <aside className="panel right">
    <div className="eyebrow">Model state</div>
    <div className="card"><h3>Identity invariants</h3><div className="metric"><span>Base body ID</span><span>{bodyId?"LOCKED":"—"}</span></div><div className="metric"><span>Body-fat mode</span><span>CONSTANT</span></div><div className="metric"><span>Future image synthesis</span><span>OFF</span></div><div className="metric"><span>Geometry source</span><span>{measurements?"PHOTO + SCALE":"DEFAULT"}</span></div></div>
    {tab==="future"&&<div className="card"><h3>Checkpoint</h3><div style={{fontSize:40,fontWeight:900,letterSpacing:"-.05em"}}>{prettyWeeks(weeks)}</div><p className="muted">Same body mesh. Local muscle controls only.</p></div>}
    <div className="card"><h3>Privacy controls</h3><p className="muted">Local prototype does not persist original photo bytes after analysis.</p><button className="ghost" style={{width:"100%"}} onClick={()=>setPhotos({})}>DELETE PHOTOS</button><button className="ghost danger" style={{width:"100%",marginTop:7}} onClick={wipe}>DELETE BODY MODEL</button><button className="ghost danger" style={{width:"100%",marginTop:7}} onClick={wipe}>DELETE ACCOUNT DATA</button></div>
    <div className="notice">Actual outcomes vary due to genetics, nutrition, sleep, recovery, hormones, technique, effort, training history, and adherence.</div>
   </aside>
  </section>
  <footer className="timeline">
   <div><strong>TRAINING TIMELINE</strong><small>{simBusy?"Recalculating adaptation…":"Smooth parameter interpolation"}</small></div>
   <div><input aria-label="Training timeline" type="range" min={0} max={52} step={1} value={weeks} onChange={e=>moveTimeline(+e.target.value)}/><div className="ticks">{checkpoints.map(w=><span key={w}>{checkpointLabel(w)}</span>)}</div></div>
   <div className="weeks">{prettyWeeks(weeks)}</div>
  </footer>
 </main>
}
