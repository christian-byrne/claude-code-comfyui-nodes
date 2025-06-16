# Zapier, n8n, and Make Workflow Knowledge Resources

## Sources:

- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/blob/master/README.md
- https://docs.n8n.io/glossary/#ai-reranking
- https://docs.n8n.io/flow-logic/
- https://docs.n8n.io/data/
- https://docs.n8n.io/integrations/creating-nodes/build/declarative-style-node/
- https://docs.n8n.io/integrations/creating-nodes/build/programmatic-style-node/
- https://docs.n8n.io/integrations/creating-nodes/build/reference/ui-elements/
- https://docs.n8n.io/integrations/creating-nodes/build/reference/node-file-structure/
- https://docs.n8n.io/integrations/creating-nodes/build/reference/ux-guidelines/
- https://docs.zapier.com/platform/reference/forms-app
- https://docs.zapier.com/platform/reference/crm-app
- https://docs.zapier.com/platform/reference/project-app
- https://docs.zapier.com/platform/reference/ai-app
- https://docs.zapier.com/platform/reference/ai-actions
- https://actions.zapier.com/
- https://docs.zapier.com/platform/quickstart/glossary
- https://docs.zapier.com/platform/quickstart/zapier-integration-structure
- https://docs.zapier.com/platform/quickstart/private-vs-public-integrations
- https://docs.zapier.com/platform/quickstart/recommended-triggers-and-actions
- https://docs.zapier.com/platform/build/field-definitions
- https://docs.zapier.com/platform/build/add-fields
- https://docs.zapier.com/platform/build/dynamic-field
- https://docs.zapier.com/platform/build/line-items
- https://docs.zapier.com/platform/build/sample-data
- https://docs.zapier.com/platform/build/response-types
- https://docs.zapier.com/platform/build/hook-trigger
- https://docs.zapier.com/platform/build/deduplication
- https://docs.zapier.com/platform/build/pagination-trigger
- https://docs.zapier.com/platform/build/cli-hook-trigger

## Additional Suggested Resources

### n8n Architecture Deep Dives
- https://github.com/n8n-io/n8n/tree/master/packages/workflow - Core workflow engine
- https://github.com/n8n-io/n8n/tree/master/packages/core - Core execution logic
- https://github.com/n8n-io/n8n/tree/master/packages/nodes-base - Example nodes implementation
- https://docs.n8n.io/hosting/architecture/ - System architecture overview

### Zapier Technical Resources
- https://docs.zapier.com/platform/build/advanced-action-field-features - Advanced field features
- https://docs.zapier.com/platform/build/hydration - Data hydration patterns
- https://docs.zapier.com/platform/build/file-handling - File handling in workflows
- https://docs.zapier.com/platform/build/cli-build-test - CLI testing patterns

### Make/Integromat Resources
- https://www.make.com/en/help/app-fundamentals - App fundamentals
- https://www.make.com/en/help/modules/types-of-modules - Module types
- https://www.make.com/en/help/scenarios - Scenario structure
- https://www.make.com/en/help/tools/flow-control - Flow control tools
- https://www.make.com/en/help/functions - Functions and expressions
- https://www.make.com/en/api-documentation - API documentation

### Workflow Execution Patterns
- https://docs.n8n.io/workflows/executions/ - n8n execution model
- https://docs.zapier.com/platform/build/task-history - Zapier task history
- https://www.make.com/en/help/scenarios/scheduling-scenarios - Make scheduling

## Architecture & Core Concepts to Research

### Zapier

- [ ] Zapier Platform Documentation
- [ ] Zapier Developer Platform docs
- [ ] Zapier CLI documentation
- [ ] Zapier Integration/App structure
- [ ] Zapier Trigger/Action architecture
- [ ] Zapier Webhooks and API patterns
- [ ] Zapier Data transformation features (Formatter, Code steps)
- [ ] Zapier Multi-step Zaps and branching logic

### n8n

- [ ] n8n Documentation (self-hosted workflow automation)
- [ ] n8n Node development documentation
- [ ] n8n Architecture overview
- [ ] n8n Workflow JSON structure
- [ ] n8n Trigger nodes vs Regular nodes
- [ ] n8n Expression language and data handling
- [ ] n8n Custom node creation guide
- [ ] n8n Webhook and API patterns

### Make (formerly Integromat)

- [ ] Make Documentation
- [ ] Make Scenario structure
- [ ] Make Module development
- [ ] Make Data structures and mapping
- [ ] Make Router and Iterator patterns
- [ ] Make Error handling and retry logic
- [ ] Make Webhooks and scheduling

## Key Areas to Focus On

1. **Node/Module/Action Architecture**

   - How do they define reusable components?
   - Input/output specifications
   - Configuration schemas

2. **Data Flow & Transformation**

   - How data passes between nodes
   - Data mapping interfaces
   - Expression languages for transformations

3. **Execution Models**

   - Trigger mechanisms (webhooks, schedules, events)
   - Sequential vs parallel execution
   - Error handling and retries

4. **Visual Programming Paradigms**

   - How they represent workflows visually
   - Connection types and constraints
   - Conditional logic and branching

5. **Integration Patterns**
   - Authentication methods
   - API abstraction layers
   - Common integration patterns

## Suggested Search Terms & Resources

### Primary Sources

- Official documentation sites
- Developer/API documentation
- GitHub repositories (n8n is open source)
- Architecture blog posts from the companies

### Secondary Sources

- Technical blog posts about building integrations
- Comparison articles between platforms
- Developer community forums
- YouTube tutorials on advanced features

### Specific URLs to Visit

- https://zapier.com/developer
- https://docs.n8n.io/
- https://www.make.com/en/help/modules
- n8n GitHub: https://github.com/n8n-io/n8n

## Questions to Answer

1. How do these platforms define and structure their "nodes" or "modules"?
2. What are the common patterns for data transformation between steps?
3. How do they handle authentication and API connections?
4. What are their execution models (synchronous, asynchronous, streaming)?
5. How do they represent conditional logic and branching?
6. What are their error handling and retry mechanisms?
7. How do they handle data types and schema validation?
8. What are their webhook and trigger architectures?

---

_Add your findings below as you research each platform_
