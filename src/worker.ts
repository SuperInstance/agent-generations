interface AgentGeneration {
  id: string;
  agentId: string;
  version: string;
  parentVersion?: string;
  timestamp: number;
  fitness: number;
  milestones: string[];
  traits: Record<string, any>;
  metadata: {
    environment: string;
    trainingCycles: number;
    createdAt: number;
  };
}

interface GenerationTree {
  agentId: string;
  rootVersion: string;
  branches: Record<string, string[]>;
  generations: AgentGeneration[];
}

interface ComparisonRequest {
  versions: string[];
  metrics: string[];
}

interface ComparisonResult {
  versions: string[];
  fitnessComparison: Record<string, number>;
  traitEvolution: Record<string, any[]>;
  performanceDelta: Record<string, number>;
}

class AgentGenerations {
  private generations: Map<string, AgentGeneration[]> = new Map();
  private trees: Map<string, GenerationTree> = new Map();

  constructor() {
    this.initializeDefaultAgent();
  }

  private initializeDefaultAgent(): void {
    const defaultGen: AgentGeneration = {
      id: "gen_001",
      agentId: "hero_agent",
      version: "1.0.0",
      timestamp: Date.now(),
      fitness: 0.85,
      milestones: ["initialization", "basic_reasoning"],
      traits: {
        reasoning: "basic",
        creativity: 0.3,
        efficiency: 0.7
      },
      metadata: {
        environment: "development",
        trainingCycles: 100,
        createdAt: Date.now()
      }
    };

    this.generations.set("hero_agent", [defaultGen]);
    
    const defaultTree: GenerationTree = {
      agentId: "hero_agent",
      rootVersion: "1.0.0",
      branches: {
        "1.0.0": []
      },
      generations: [defaultGen]
    };

    this.trees.set("hero_agent", defaultTree);
  }

  async getGenerations(agentId: string): Promise<AgentGeneration[]> {
    const gens = this.generations.get(agentId);
    if (!gens) {
      throw new Error(`Agent ${agentId} not found`);
    }
    return gens.sort((a, b) => b.timestamp - a.timestamp);
  }

  async getTree(agentId?: string): Promise<GenerationTree | GenerationTree[]> {
    if (agentId) {
      const tree = this.trees.get(agentId);
      if (!tree) {
        throw new Error(`Tree for agent ${agentId} not found`);
      }
      return tree;
    }
    return Array.from(this.trees.values());
  }

  async compareGenerations(request: ComparisonRequest): Promise<ComparisonResult> {
    const allGenerations = Array.from(this.generations.values()).flat();
    const selectedGens = allGenerations.filter(gen => 
      request.versions.includes(gen.version)
    ).sort((a, b) => a.timestamp - b.timestamp);

    if (selectedGens.length < 2) {
      throw new Error("At least two versions required for comparison");
    }

    const fitnessComparison: Record<string, number> = {};
    const traitEvolution: Record<string, any[]> = {};
    const performanceDelta: Record<string, number> = {};

    selectedGens.forEach((gen, index) => {
      fitnessComparison[gen.version] = gen.fitness;
      
      request.metrics.forEach(metric => {
        if (!traitEvolution[metric]) {
          traitEvolution[metric] = [];
        }
        traitEvolution[metric].push(gen.traits[metric] || 0);
      });

      if (index > 0) {
        const prevGen = selectedGens[index - 1];
        performanceDelta[gen.version] = gen.fitness - prevGen.fitness;
      }
    });

    return {
      versions: selectedGens.map(gen => gen.version),
      fitnessComparison,
      traitEvolution,
      performanceDelta
    };
  }

  async addGeneration(generation: Omit<AgentGeneration, "id" | "timestamp">): Promise<AgentGeneration> {
    const newGen: AgentGeneration = {
      ...generation,
      id: `gen_${Date.now().toString(36)}`,
      timestamp: Date.now()
    };

    if (!this.generations.has(generation.agentId)) {
      this.generations.set(generation.agentId, []);
    }

    const agentGens = this.generations.get(generation.agentId)!;
    agentGens.push(newGen);

    this.updateTree(generation.agentId, newGen);

    return newGen;
  }

  private updateTree(agentId: string, newGen: AgentGeneration): void {
    let tree = this.trees.get(agentId);
    
    if (!tree) {
      tree = {
        agentId,
        rootVersion: newGen.version,
        branches: {},
        generations: []
      };
    }

    tree.generations.push(newGen);

    if (newGen.parentVersion) {
      if (!tree.branches[newGen.parentVersion]) {
        tree.branches[newGen.parentVersion] = [];
      }
      tree.branches[newGen.parentVersion].push(newGen.version);
    } else {
      tree.rootVersion = newGen.version;
    }

    this.trees.set(agentId, tree);
  }

  async getFitnessHistory(agentId: string): Promise<{timestamps: number[], fitness: number[]}> {
    const gens = await this.getGenerations(agentId);
    return {
      timestamps: gens.map(gen => gen.timestamp),
      fitness: gens.map(gen => gen.fitness)
    };
  }
}

const agentGenerations = new AgentGenerations();

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
  "Content-Type": "application/json"
};

async function handleRequest(request: Request): Promise<Response> {
  const url = new URL(request.url);
  const path = url.pathname;

  if (request.method === "OPTIONS") {
    return new Response(null, {
      headers: corsHeaders
    });
  }

  if (path === "/health") {
    return new Response(JSON.stringify({ status: "healthy", service: "Agent Generations" }), {
      headers: corsHeaders
    });
  }

  if (path.startsWith("/api/generations/")) {
    const agentId = path.split("/api/generations/")[1];
    try {
      const generations = await agentGenerations.getGenerations(agentId);
      return new Response(JSON.stringify(generations), {
        headers: corsHeaders
      });
    } catch (error) {
      return new Response(JSON.stringify({ error: (error as Error).message }), {
        status: 404,
        headers: corsHeaders
      });
    }
  }

  if (path === "/api/tree") {
    const agentId = url.searchParams.get("agentId");
    try {
      const tree = await agentGenerations.getTree(agentId || undefined);
      return new Response(JSON.stringify(tree), {
        headers: corsHeaders
      });
    } catch (error) {
      return new Response(JSON.stringify({ error: (error as Error).message }), {
        status: 404,
        headers: corsHeaders
      });
    }
  }

  if (path === "/api/compare" && request.method === "POST") {
    try {
      const body = await request.json() as ComparisonRequest;
      const result = await agentGenerations.compareGenerations(body);
      return new Response(JSON.stringify(result), {
        headers: corsHeaders
      });
    } catch (error) {
      return new Response(JSON.stringify({ error: (error as Error).message }), {
        status: 400,
        headers: corsHeaders
      });
    }
  }

  if (path === "/api/fitness" && request.method === "GET") {
    const agentId = url.searchParams.get("agentId");
    if (!agentId) {
      return new Response(JSON.stringify({ error: "agentId parameter required" }), {
        status: 400,
        headers: corsHeaders
      });
    }
    try {
      const history = await agentGenerations.getFitnessHistory(agentId);
      return new Response(JSON.stringify(history), {
        headers: corsHeaders
      });
    } catch (error) {
      return new Response(JSON.stringify({ error: (error as Error).message }), {
        status: 404,
        headers: corsHeaders
      });
    }
  }

  if (path === "/api/generations" && request.method === "POST") {
    try {
      const body = await request.json() as Omit<AgentGeneration, "id" | "timestamp">;
      const newGen = await agentGenerations.addGeneration(body);
      return new Response(JSON.stringify(newGen), {
        status: 201,
        headers: corsHeaders
      });
    } catch (error) {
      return new Response(JSON.stringify({ error: (error as Error).message }), {
        status: 400,
        headers: corsHeaders
      });
    }
  }

  return new Response(JSON.stringify({ 
    error: "Not found",
    endpoints: [
      "GET /api/generations/:agentId",
      "GET /api/tree?agentId=",
      "POST /api/compare",
      "GET /api/fitness?agentId=",
      "POST /api/generations",
      "GET /health"
    ]
  }), {
    status: 404,
    headers: corsHeaders
  });
}

const worker: ExportedHandler = {
  async fetch(request: Request): Promise<Response> {
    return handleRequest(request);
  }
};
const sh={"Content-Security-Policy":"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; frame-ancestors 'none'","X-Frame-Options":"DENY"};
export default{async fetch(r:Request){const u=new URL(r.url);if(u.pathname==='/health')return new Response(JSON.stringify({status:"ok"}),{headers:{"Content-Type":"application/json",...sh}});return new Response(html,{headers:{"Content-Type":"text/html;charset=UTF-8",...sh}});}};