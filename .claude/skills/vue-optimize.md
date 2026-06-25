# Vue Component Optimizer

Analyzes Vue 3 components for performance optimizations and code reuse opportunities.

## Usage

```bash
/vue-optimize [component-path]
```

If no path is provided, analyzes all Vue components in the project.

## What This Skill Does

1. **Performance Analysis**
   - Identifies missing computed properties (calculations in methods/template)
   - Detects unnecessary re-renders (missing v-show vs v-if optimization)
   - Finds heavy operations in templates
   - Checks for missing keys in v-for loops
   - Identifies opportunities for lazy loading

2. **Code Reuse Analysis**
   - Finds repeated logic patterns across components
   - Suggests extractable composables
   - Identifies duplicate computed properties
   - Detects similar component structures

3. **Best Practices**
   - Validates Composition API usage
   - Checks for proper reactivity patterns
   - Identifies prop mutation issues
   - Validates event emission patterns

## Instructions

When this skill is invoked:

1. **Discovery Phase**
   - If a specific component path is provided, analyze that component
   - Otherwise, find all `.vue` files: `find client/src -name "*.vue" -type f`
   - Read each component file completely

2. **Analysis Phase**

   For each component, check:

   **Performance Issues:**
   - Look for calculations in methods that should be computed properties
   - Find filter operations in templates that should be computed
   - Check for missing `key` attributes in `v-for` loops
   - Identify unnecessary watchers (could be computed instead)
   - Find heavy operations (sorting, filtering) done on every render
   - Check for large data arrays that could be paginated or virtualized

   **Reactivity Issues:**
   - Look for direct prop mutations
   - Check if `.value` is used correctly in script vs template
   - Identify refs that could be readonly or computed
   - Find watch callbacks that could be computed properties

   **Code Reuse Opportunities:**
   - Compare components to find repeated logic patterns
   - Identify API calls that could be in a composable
   - Find duplicated computed properties across components
   - Look for similar data fetching patterns
   - Detect repeated state management logic

   **Composition API Best Practices:**
   - Check if lifecycle hooks are used appropriately
   - Validate that refs/computed/watch are imported from 'vue'
   - Ensure composables return reactive references
   - Check for proper setup() return patterns

3. **Report Phase**

   Generate a structured report with:

   ```markdown
   ## Vue Component Analysis Report

   ### Summary
   - Total components analyzed: X
   - Performance issues found: Y
   - Code reuse opportunities: Z
   - Best practice violations: W

   ### Critical Issues (High Priority)
   [List issues that significantly impact performance]

   ### Performance Optimizations

   #### Component: [Name]
   **Issue:** [Description]
   **Location:** [File path:line number]
   **Current Code:**
   ```vue
   [problematic code snippet]
   ```
   **Suggested Fix:**
   ```vue
   [optimized code]
   ```
   **Impact:** [Performance benefit]
   **Priority:** High/Medium/Low

   ### Code Reuse Opportunities

   #### Extractable Composable: [Name]
   **Pattern Found In:**
   - [Component 1] - [file:line]
   - [Component 2] - [file:line]
   
   **Repeated Logic:**
   ```javascript
   [common code pattern]
   ```
   
   **Suggested Composable:**
   ```javascript
   // composables/use[Name].js
   import { ref, computed } from 'vue'
   
   export function use[Name]() {
     // Extracted logic here
     return {
       // Exported refs/methods
     }
   }
   ```
   
   **Benefit:** Reduces duplication, improves maintainability

   ### Best Practice Recommendations

   #### Component: [Name]
   **Issue:** [Violation description]
   **Recommendation:** [How to fix]
   **Reference:** [Vue docs link if applicable]

   ### Summary of Changes

   **Estimated Performance Gain:** [percentage or description]
   **Code Reduction:** [lines of code that can be eliminated]
   **Maintainability:** [improvement description]
   ```

4. **Specific Checks to Perform**

   **In `<template>` section:**
   - [ ] Check for complex expressions that should be computed
   - [ ] Find `.filter()`, `.map()`, `.reduce()` calls in template
   - [ ] Look for missing `:key` in `v-for`
   - [ ] Identify `v-if` on expensive renders (suggest `v-show`)
   - [ ] Find repeated component structures

   **In `<script setup>` or `setup()`:**
   - [ ] Look for calculations in methods instead of computed
   - [ ] Find refs that never change (should be readonly/computed)
   - [ ] Check for watch when computed would work
   - [ ] Identify API calls that could be extracted
   - [ ] Look for repeated state management patterns
   - [ ] Check for props being mutated directly
   - [ ] Find duplicate computed properties

   **Cross-component analysis:**
   - [ ] Compare data fetching patterns
   - [ ] Find similar state management logic
   - [ ] Identify common form handling patterns
   - [ ] Look for repeated validation logic
   - [ ] Find similar filter/search implementations

5. **Prioritization**

   Rate each issue by:
   - **High Priority:** Causes unnecessary re-renders, blocks main thread, missing keys
   - **Medium Priority:** Suboptimal patterns, could use computed instead of watch
   - **Low Priority:** Code style, minor optimizations

6. **Code Examples**

   For each suggestion, provide:
   - Current problematic code (exact snippet from file)
   - Optimized version with explanation
   - Expected performance benefit

## Example Output Format

```markdown
# Vue Component Optimization Report
Generated: 2024-01-15

## Executive Summary
- Analyzed: 12 components
- Critical issues: 3
- Performance opportunities: 8
- Code reuse opportunities: 5

## Critical Performance Issues

### 1. Missing v-for keys in RestockingView.vue:52
**Severity:** HIGH
**Impact:** Unpredictable re-rendering behavior

Current:
```vue
<tr v-for="item in recommendedItems">
```

Fix:
```vue
<tr v-for="item in recommendedItems" :key="item.sku">
```

### 2. Heavy calculation in template - Orders.vue:78
**Severity:** HIGH  
**Impact:** Recalculates on every render

Current:
```vue
{{ orders.filter(o => o.status === 'Delivered').length }}
```

Fix:
```javascript
const deliveredCount = computed(() => 
  orders.value.filter(o => o.status === 'Delivered').length
)
```

## Code Reuse Opportunities

### Extract API Loading Pattern
**Found in:** Dashboard.vue, Orders.vue, Inventory.vue

Pattern:
```javascript
const loading = ref(true)
const error = ref(null)
const data = ref([])

const loadData = async () => {
  try {
    loading.value = true
    data.value = await api.getData()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
```

**Suggested Composable:**
```javascript
// composables/useAsyncData.js
export function useAsyncData(fetchFn) {
  const loading = ref(false)
  const error = ref(null)
  const data = ref(null)

  const execute = async (...args) => {
    loading.value = true
    error.value = null
    try {
      data.value = await fetchFn(...args)
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  return { loading, error, data, execute }
}
```

**Usage:**
```javascript
const { loading, error, data, execute } = useAsyncData(api.getOrders)
onMounted(() => execute())
```

**Benefit:** Eliminates 20+ lines of duplicate code across 5 components

## Next Steps
1. Address all HIGH priority issues (3 fixes)
2. Extract useAsyncData composable (affects 5 components)
3. Implement remaining computed properties (8 optimizations)
4. Review and apply LOW priority suggestions
```

## Important Notes

- Focus on Vue 3 Composition API patterns
- Reference the client/CLAUDE.md file for project-specific patterns
- Provide actionable, copy-paste ready code fixes
- Prioritize issues by performance impact
- Include line numbers for all findings
- Cross-reference multiple components to find patterns
- Be specific - no generic advice without concrete examples
