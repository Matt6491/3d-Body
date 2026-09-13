# FORM Project Instructions

FORM must not contain or call:
window.ethereum
ethereum.request
eth_requestAccounts
MetaMask
WalletConnect
wagmi
ethers
web3

FORM must never request a crypto-wallet connection.
FORM authentication should eventually use normal account authentication such as email, Google, or Apple.

## Preserved Architecture
- Next.js / TypeScript
- React Three Fiber / Three.js
- Deterministic MuscleAdaptationEngine (physiology logic never moved into React or replaced with LLM)
- Exercise Database
- ParametricPrimitiveBodyProvider (BodyModelProvider abstraction)
- Local silhouette analysis with front-only photo support + optional side/back depth refinement
