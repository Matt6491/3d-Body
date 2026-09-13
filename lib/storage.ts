import crypto from "crypto";

export interface StoredBody {
  accountRef: string | null;
  mesh: any;
  profile: any;
}

export interface StoredAnalysis {
  accountRef: string | null;
  analysis: any;
}

class InMemoryBodyRepository {
  private bodies = new Map<string, StoredBody>();
  private analyses = new Map<string, StoredAnalysis>();

  saveBody(accountRef: string | null, body: any, profile: any): string {
    const key = crypto.randomUUID();
    this.bodies.set(key, { accountRef, mesh: body, profile });
    return key;
  }

  getBody(bodyId: string): StoredBody | undefined {
    return this.bodies.get(bodyId);
  }

  deleteBody(bodyId: string): boolean {
    return this.bodies.delete(bodyId);
  }

  saveAnalysis(accountRef: string | null, analysis: any): string {
    const key = crypto.randomUUID();
    this.analyses.set(key, { accountRef, analysis });
    return key;
  }

  deleteAnalysis(analysisId: string): boolean {
    return this.analyses.delete(analysisId);
  }

  deleteAccountData(accountRef: string): { bodies: number; analyses: number } {
    let bCount = 0;
    let aCount = 0;
    for (const [k, v] of this.bodies.entries()) {
      if (v.accountRef === accountRef) {
        this.bodies.delete(k);
        bCount++;
      }
    }
    for (const [k, v] of this.analyses.entries()) {
      if (v.accountRef === accountRef) {
        this.analyses.delete(k);
        aCount++;
      }
    }
    return { bodies: bCount, analyses: aCount };
  }
}

export const repo = new InMemoryBodyRepository();
