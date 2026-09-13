
import {emptyMuscles,Exercise,MuscleValues} from "./types";
export const API=process.env.NEXT_PUBLIC_FORM_API || "/api";
export async function getExercises():Promise<Exercise[]>{const r=await fetch(`${API}/exercises`);if(!r.ok)throw new Error("Exercise database unavailable");return r.json()}
export async function analyzeBody(form:FormData){const r=await fetch(`${API}/analyze`,{method:"POST",body:form});if(!r.ok)throw new Error((await r.json()).detail||"Photo analysis failed");return r.json()}
export async function simulate(workout:any[],weeks:number,profile:any):Promise<{muscles:MuscleValues;bodyFatDelta:number}>{
 const r=await fetch(`${API}/simulate`,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({...profile,weeks,workout})});
 if(!r.ok)throw new Error("Simulation failed");return r.json()
}
export async function deleteBody(id:string){await fetch(`${API}/body/${id}`,{method:"DELETE"})}
export async function deleteAnalysis(id:string){await fetch(`${API}/analysis/${id}`,{method:"DELETE"})}

export type TimelineState={weeks:number;muscles:MuscleValues;bodyFatDelta:number};
export async function simulateTimeline(workout:any[],profile:any):Promise<TimelineState[]>{
 const r=await fetch(`${API}/simulate/timeline`,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({...profile,weeks:52,workout})});
 if(!r.ok)throw new Error("Timeline simulation failed");
 const j=await r.json(); return j.checkpoints;
}
export function interpolateTimeline(states:TimelineState[],weeks:number):MuscleValues{
 if(!states.length)return emptyMuscles();
 if(weeks<=states[0].weeks)return states[0].muscles;
 if(weeks>=states[states.length-1].weeks)return states[states.length-1].muscles;
 const hi=states.findIndex(s=>s.weeks>=weeks), lo=Math.max(0,hi-1);
 const a=states[lo],b=states[hi]; const raw=(weeks-a.weeks)/(b.weeks-a.weeks);
 const t=raw*raw*(3-2*raw);
 return Object.fromEntries(Object.keys(a.muscles).map(k=>[k,a.muscles[k as keyof MuscleValues]+(b.muscles[k as keyof MuscleValues]-a.muscles[k as keyof MuscleValues])*t])) as MuscleValues;
}
