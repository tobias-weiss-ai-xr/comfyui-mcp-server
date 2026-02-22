/**
 * ComfyUI Workflow Memory Skill
 * 
 * Preserves and recalls knowledge about ComfyUI workflows
 * Enables persistent memory of generation parameters, prompts, and history
 */

import { z } from 'zod';
import fs from 'fs/promises';
import path from 'path';

// Schema definitions
const GenerationRecordSchema = z.object({
  id: z.string(),
  timestamp: z.string(),
  workflow: z.string(),
  prompt: z.string(),
  width: z.number(),
  height: z.number(),
  asset_id: z.string().optional(),
  filename: z.string().optional(),
  success: z.boolean(),
  tags: z.array(z.string()).optional(),
});

const PromptTemplateSchema = z.object({
  id: z.string(),
  prompt: z.string(),
  name: z.string().optional(),
  category: z.string(),
  tags: z.array(z.string()),
  rating: z.number().min(1).max(5).default(3),
  use_count: z.number().default(0),
  last_used: z.string().optional(),
  notes: z.string().optional(),
});

const WorkflowConfigSchema = z.object({
  name: z.string(),
  description: z.string().optional(),
  default_params: z.object({
    width: z.number().default(1024),
    height: z.number().default(576),
    return_inline_preview: z.boolean().default(true),
  }),
  optimal_settings: z.record(z.object({
    width: z.number(),
    height: z.number(),
  })).optional(),
  tags: z.array(z.string()).optional(),
});

const WorkflowMemorySchema = z.object({
  version: z.string().default('1.0.0'),
  last_updated: z.string(),
  current_session: z.object({
    active_workflow: z.string().default('zai_small'),
    default_resolution: z.object({
      width: z.number().default(1920),
      height: z.number().default(1080),
    }),
    last_prompt: z.string().optional(),
    generation_count: z.number().default(0),
    session_start: z.string(),
  }),
  prompt_library: z.record(z.array(PromptTemplateSchema)),
  generation_history: z.array(GenerationRecordSchema),
  workflow_configs: z.record(WorkflowConfigSchema),
  learned_patterns: z.object({
    effective_keyword_combos: z.array(z.array(z.string())),
    style_modifiers: z.record(z.array(z.string())),
    avoid_patterns: z.array(z.string()).optional(),
  }),
  favorites: z.object({
    prompts: z.array(z.string()),
    assets: z.array(z.string()),
    workflows: z.array(z.string()),
  }),
});

type WorkflowMemory = z.infer<typeof WorkflowMemorySchema>;
type GenerationRecord = z.infer<typeof GenerationRecordSchema>;
type PromptTemplate = z.infer<typeof PromptTemplateSchema>;
type WorkflowConfig = z.infer<typeof WorkflowConfigSchema>;

// Default memory structure
const DEFAULT_MEMORY: WorkflowMemory = {
  version: '1.0.0',
  last_updated: new Date().toISOString(),
  current_session: {
    active_workflow: 'zai_small',
    default_resolution: { width: 1920, height: 1080 },
    generation_count: 0,
    session_start: new Date().toISOString(),
  },
  prompt_library: {
    'architecture_dub_techno': [
      {
        id: 'arch-dt-001',
        prompt: 'brutalist concrete tower at night, fog and mist, single amber light, bass vibrations distorting the structure, dub techno atmosphere, cold industrial minimal, cinematic',
        name: 'Brutalist Tower Night',
        category: 'architecture_dub_techno',
        tags: ['architecture', 'dub-techno', 'industrial', 'brutalist', 'night'],
        rating: 5,
        use_count: 1,
      },
      {
        id: 'arch-dt-002',
        prompt: 'endless concrete corridor with repeating arches, fading into darkness, single red emergency light, sub-bass vibrations distorting perspective, industrial dub techno minimalism, cold atmosphere',
        name: 'Infinite Corridor',
        category: 'architecture_dub_techno',
        tags: ['architecture', 'corridor', 'dub-techno', 'minimal', 'industrial'],
        rating: 5,
        use_count: 1,
      },
      {
        id: 'arch-dt-003',
        prompt: 'abandoned power station with massive turbine hall, rusted machinery sculptures, shafts of light through broken windows, industrial decay, heavy bass echo atmosphere, dub techno urban exploration aesthetic',
        name: 'Abandoned Power Station',
        category: 'architecture_dub_techno',
        tags: ['architecture', 'industrial', 'decay', 'dub-techno', 'machinery'],
        rating: 5,
        use_count: 1,
      },
    ],
    'sculpture_abstract': [
      {
        id: 'sculpt-abs-001',
        prompt: 'giant geometric sculpture floating in void, black monolith with pulsing edges, echo and reverb visual effects, dub techno sound made visible, dark minimal aesthetic, abstract architecture',
        name: 'Floating Monolith',
        category: 'sculpture_abstract',
        tags: ['sculpture', 'abstract', 'monolith', 'geometric', 'dub-techno'],
        rating: 5,
        use_count: 1,
      },
      {
        id: 'sculpt-abs-002',
        prompt: 'massive abstract sculpture in empty plaza, metallic surface reflecting neon lights, mist and fog, deep bass atmosphere, dark minimal dub techno aesthetic, cinematic lighting',
        name: 'Plaza Sculpture',
        category: 'sculpture_abstract',
        tags: ['sculpture', 'abstract', 'neon', 'minimal', 'plaza'],
        rating: 4,
        use_count: 1,
      },
    ],
    'classical_art': [
      {
        id: 'class-001',
        prompt: 'ancient Greek temple ruins at golden hour, massive marble columns, dramatic shadows, overgrown with ivy, cinematic atmosphere, archaeological masterpiece',
        name: 'Greek Temple Ruins',
        category: 'classical_art',
        tags: ['classical', 'architecture', 'greek', 'ruins', 'golden-hour'],
        rating: 5,
        use_count: 1,
      },
    ],
  },
  generation_history: [],
  workflow_configs: {
    'zai_small': {
      name: 'zai_small',
      description: 'Fast SDXL generation workflow optimized for quick iterations',
      default_params: {
        width: 1024,
        height: 576,
        return_inline_preview: true,
      },
      optimal_settings: {
        'cinematic_1080p': { width: 1920, height: 1080 },
        'cinematic_4k': { width: 3840, height: 2160 },
        'square': { width: 1024, height: 1024 },
        'portrait': { width: 896, height: 1152 },
        'landscape_wide': { width: 1344, height: 768 },
      },
      tags: ['fast', 'sdxl', 'versatile'],
    },
  },
  learned_patterns: {
    effective_keyword_combos: [
      ['dub techno', 'concrete', 'bass visualization'],
      ['architecture', 'sculpture', 'minimal'],
      ['brutalist', 'fog', 'single light'],
      ['industrial', 'decay', 'echo'],
    ],
    style_modifiers: {
      'dark_moody': ['cold', 'dark', 'minimal', 'industrial', 'fog', 'mist'],
      'cinematic': ['cinematic', 'dramatic lighting', 'atmospheric', 'golden hour'],
      'dub_techno': ['bass vibrations', 'echo', 'reverb', 'sub-bass', 'cold'],
      'architectural': ['concrete', 'brutalist', 'geometric', 'monumental'],
    },
    avoid_patterns: [],
  },
  favorites: {
    prompts: [],
    assets: [],
    workflows: ['zai_small'],
  },
};

/**
 * Workflow Memory Manager Class
 */
export class WorkflowMemoryManager {
  private memoryPath: string;
  private memory: WorkflowMemory;
  
  constructor(memoryDir: string = './data') {
    this.memoryPath = path.join(memoryDir, 'comfyui-workflow-memory.json');
    this.memory = DEFAULT_MEMORY;
  }
  
  /**
   * Initialize or load memory from disk
   */
  async initialize(): Promise<void> {
    try {
      const data = await fs.readFile(this.memoryPath, 'utf-8');
      this.memory = WorkflowMemorySchema.parse(JSON.parse(data));
    } catch {
      // File doesn't exist, use defaults
      await this.save();
    }
  }
  
  /**
   * Save memory to disk
   */
  async save(): Promise<void> {
    this.memory.last_updated = new Date().toISOString();
    await fs.mkdir(path.dirname(this.memoryPath), { recursive: true });
    await fs.writeFile(this.memoryPath, JSON.stringify(this.memory, null, 2));
  }
  
  /**
   * Record a new generation
   */
  recordGeneration(record: Partial<GenerationRecord>): GenerationRecord {
    const fullRecord: GenerationRecord = {
      id: record.id || crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      workflow: record.workflow || this.memory.current_session.active_workflow,
      prompt: record.prompt || '',
      width: record.width || this.memory.current_session.default_resolution.width,
      height: record.height || this.memory.current_session.default_resolution.height,
      success: record.success ?? true,
      asset_id: record.asset_id,
      filename: record.filename,
      tags: record.tags,
    };
    
    this.memory.generation_history.unshift(fullRecord);
    this.memory.current_session.generation_count++;
    this.memory.current_session.last_prompt = fullRecord.prompt;
    
    // Keep only last 1000 generations
    if (this.memory.generation_history.length > 1000) {
      this.memory.generation_history = this.memory.generation_history.slice(0, 1000);
    }
    
    return fullRecord;
  }
  
  /**
   * Add a prompt to the library
   */
  addPromptTemplate(category: string, template: Omit<PromptTemplate, 'id' | 'use_count'>): PromptTemplate {
    const fullTemplate: PromptTemplate = {
      ...template,
      id: crypto.randomUUID(),
      category,
      use_count: 0,
      last_used: new Date().toISOString(),
    };
    
    if (!this.memory.prompt_library[category]) {
      this.memory.prompt_library[category] = [];
    }
    
    this.memory.prompt_library[category].push(fullTemplate);
    return fullTemplate;
  }
  
  /**
   * Get prompts by category
   */
  getPromptsByCategory(category: string): PromptTemplate[] {
    return this.memory.prompt_library[category] || [];
  }
  
  /**
   * Search prompts by tags or keywords
   */
  searchPrompts(query: string): PromptTemplate[] {
    const queryLower = query.toLowerCase();
    const results: PromptTemplate[] = [];
    
    for (const category of Object.keys(this.memory.prompt_library)) {
      for (const template of this.memory.prompt_library[category]) {
        if (
          template.prompt.toLowerCase().includes(queryLower) ||
          template.tags.some(tag => tag.toLowerCase().includes(queryLower)) ||
          template.name?.toLowerCase().includes(queryLower)
        ) {
          results.push(template);
        }
      }
    }
    
    return results.sort((a, b) => b.rating - a.rating);
  }
  
  /**
   * Get top-rated prompts
   */
  getTopPrompts(limit: number = 10): PromptTemplate[] {
    const allPrompts: PromptTemplate[] = [];
    for (const category of Object.keys(this.memory.prompt_library)) {
      allPrompts.push(...this.memory.prompt_library[category]);
    }
    return allPrompts.sort((a, b) => b.rating - a.rating).slice(0, limit);
  }
  
  /**
   * Get workflow configuration
   */
  getWorkflowConfig(workflowName: string): WorkflowConfig | undefined {
    return this.memory.workflow_configs[workflowName];
  }
  
  /**
   * Get optimal resolution for a style
   */
  getOptimalResolution(workflowName: string, style: string): { width: number; height: number } {
    const config = this.memory.workflow_configs[workflowName];
    if (config?.optimal_settings?.[style]) {
      return config.optimal_settings[style];
    }
    return this.memory.current_session.default_resolution;
  }
  
  /**
   * Get generation history
   */
  getHistory(limit: number = 50): GenerationRecord[] {
    return this.memory.generation_history.slice(0, limit);
  }
  
  /**
   * Get current session info
   */
  getCurrentSession(): WorkflowMemory['current_session'] {
    return { ...this.memory.current_session };
  }
  
  /**
   * Get style modifiers for a style category
   */
  getStyleModifiers(style: string): string[] {
    return this.memory.learned_patterns.style_modifiers[style] || [];
  }
  
  /**
   * Get effective keyword combinations
   */
  getEffectiveKeywordCombos(): string[][] {
    return this.memory.learned_patterns.effective_keyword_combos;
  }
  
  /**
   * Add to favorites
   */
  addToFavorite(type: 'prompts' | 'assets' | 'workflows', item: string): void {
    if (!this.memory.favorites[type].includes(item)) {
      this.memory.favorites[type].push(item);
    }
  }
  
  /**
   * Rate a prompt template
   */
  ratePrompt(category: string, promptId: string, rating: number): boolean {
    const templates = this.memory.prompt_library[category];
    if (!templates) return false;
    
    const template = templates.find(t => t.id === promptId);
    if (!template) return false;
    
    template.rating = Math.max(1, Math.min(5, rating));
    return true;
  }
  
  /**
   * Get full memory state (for debugging/export)
   */
  getFullMemory(): WorkflowMemory {
    return JSON.parse(JSON.stringify(this.memory));
  }
  
  /**
   * Export memory to JSON string
   */
  exportMemory(): string {
    return JSON.stringify(this.memory, null, 2);
  }
  
  /**
   * Import memory from JSON string
   */
  async importMemory(json: string): Promise<void> {
    const parsed = JSON.parse(json);
    this.memory = WorkflowMemorySchema.parse(parsed);
    await this.save();
  }
  
  /**
   * Get statistics about the memory
   */
  getStatistics(): {
    totalGenerations: number;
    sessionGenerations: number;
    promptCategories: number;
    totalPrompts: number;
    averageRating: number;
  } {
    let totalPrompts = 0;
    let totalRating = 0;
    let ratedCount = 0;
    
    for (const category of Object.keys(this.memory.prompt_library)) {
      const prompts = this.memory.prompt_library[category];
      totalPrompts += prompts.length;
      for (const p of prompts) {
        totalRating += p.rating;
        ratedCount++;
      }
    }
    
    return {
      totalGenerations: this.memory.generation_history.length,
      sessionGenerations: this.memory.current_session.generation_count,
      promptCategories: Object.keys(this.memory.prompt_library).length,
      totalPrompts,
      averageRating: ratedCount > 0 ? totalRating / ratedCount : 0,
    };
  }
}

// Export singleton instance
export const workflowMemory = new WorkflowMemoryManager();
