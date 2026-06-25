<template>
  <div class="restocking">
    <div class="page-header">
      <h2>Restocking</h2>
      <p>Plan and submit restocking orders based on demand forecasts</p>
    </div>

    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div class="card budget-card">
        <h3 class="card-title">Budget</h3>
        <div class="budget-slider-container">
          <input
            type="range"
            v-model.number="budget"
            min="10000"
            max="500000"
            step="5000"
            class="budget-slider"
          />
          <div class="budget-display">${{ budget.toLocaleString() }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Recommended Items (Highest Demand First)</h3>
          <div class="total-cost">
            <span>Total: <strong>${{ totalCost.toLocaleString() }}</strong> / ${{ budget.toLocaleString() }}</span>
            <span v-if="budgetRemaining >= 0" class="budget-remaining">(${{ budgetRemaining.toLocaleString() }} remaining)</span>
            <span v-else class="budget-exceeded">(Over budget by ${{ Math.abs(budgetRemaining).toLocaleString() }})</span>
          </div>
        </div>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>SKU</th>
                <th>Product</th>
                <th>Category</th>
                <th>Forecast Demand</th>
                <th>Unit Price</th>
                <th>Total Cost</th>
                <th>Lead Time</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="recommendedItems.length === 0">
                <td colspan="7" class="no-items">No items fit within the current budget. Try increasing the budget.</td>
              </tr>
              <tr v-for="item in recommendedItems" :key="item.sku">
                <td><strong>{{ item.sku }}</strong></td>
                <td>{{ item.name }}</td>
                <td>{{ item.category }}</td>
                <td>{{ item.forecasted_demand }}</td>
                <td>${{ item.unit_cost.toFixed(2) }}</td>
                <td><strong>${{ item.total_cost.toLocaleString() }}</strong></td>
                <td>{{ item.lead_time }} days</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="action-section">
          <button
            class="place-order-btn"
            @click="placeOrder"
            :disabled="recommendedItems.length === 0"
          >
            Place Restocking Order ({{ recommendedItems.length }} items)
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { useSubmittedOrders } from '../composables/useSubmittedOrders'

export default {
  name: 'RestockingView',
  setup() {
    const router = useRouter()
    const { submitRestockingOrder } = useSubmittedOrders()

    const loading = ref(true)
    const error = ref(null)
    const budget = ref(100000) // Default budget $100K
    const demandData = ref([])
    const inventoryData = ref([])

    // Lead times by category in days
    const leadTimes = {
      'Circuit Boards': 10,
      'Sensors': 7,
      'Actuators': 14,
      'Controllers': 12,
      'Power Supplies': 9
    }

    // Join demand and inventory data, calculate costs
    const enrichedItems = computed(() => {
      const inventoryMap = new Map(inventoryData.value.map(item => [item.sku, item]))

      return demandData.value
        .map(demand => {
          const inventory = inventoryMap.get(demand.item_sku)
          if (!inventory) return null

          const totalCost = demand.forecasted_demand * inventory.unit_cost
          const leadTime = leadTimes[inventory.category] || 10

          return {
            sku: demand.item_sku,
            name: demand.item_name,
            category: inventory.category,
            forecasted_demand: demand.forecasted_demand,
            unit_cost: inventory.unit_cost,
            total_cost: totalCost,
            lead_time: leadTime
          }
        })
        .filter(item => item !== null)
        .sort((a, b) => b.forecasted_demand - a.forecasted_demand)
    })

    // Filter items that fit within budget (running total)
    const recommendedItems = computed(() => {
      const items = []
      let runningTotal = 0

      for (const item of enrichedItems.value) {
        if (runningTotal + item.total_cost <= budget.value) {
          items.push(item)
          runningTotal += item.total_cost
        }
      }

      return items
    })

    // Calculate total cost of recommended items
    const totalCost = computed(() => {
      return recommendedItems.value.reduce((sum, item) => sum + item.total_cost, 0)
    })

    // Calculate remaining budget
    const budgetRemaining = computed(() => {
      return budget.value - totalCost.value
    })

    // Load data from API
    const loadData = async () => {
      loading.value = true
      error.value = null

      try {
        const [demand, inventory] = await Promise.all([
          api.getDemandForecasts(),
          api.getInventory()
        ])

        demandData.value = demand
        inventoryData.value = inventory
      } catch (err) {
        error.value = 'Failed to load data: ' + err.message
        console.error('Load error:', err)
      } finally {
        loading.value = false
      }
    }

    // Calculate delivery date based on category lead time
    const calculateDeliveryDate = (category, orderDate) => {
      const days = leadTimes[category] || 10
      const delivery = new Date(orderDate)
      delivery.setDate(delivery.getDate() + days)
      return delivery.toISOString()
    }

    // Place restocking order
    const placeOrder = () => {
      if (recommendedItems.value.length === 0) return

      const orderDate = new Date()
      const firstItemCategory = recommendedItems.value[0].category

      const order = {
        id: `RESTOCK-${Date.now()}-${Math.random().toString(36).substr(2, 4).toUpperCase()}`,
        budget: totalCost.value,
        items: recommendedItems.value,
        status: 'Submitted',
        orderDate: orderDate.toISOString(),
        deliveryDate: calculateDeliveryDate(firstItemCategory, orderDate)
      }

      submitRestockingOrder(order)

      // Navigate to orders page to see the submitted order
      router.push('/orders')
    }

    onMounted(loadData)

    return {
      loading,
      error,
      budget,
      recommendedItems,
      totalCost,
      budgetRemaining,
      placeOrder
    }
  }
}
</script>

<style scoped>
.restocking {
  padding: 0;
}

.budget-card {
  margin-bottom: 1.5rem;
}

.budget-slider-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}

.budget-slider {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: #e2e8f0;
  outline: none;
  -webkit-appearance: none;
  appearance: none;
  cursor: pointer;
}

.budget-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #2563eb;
  cursor: pointer;
  transition: all 0.2s ease;
}

.budget-slider::-webkit-slider-thumb:hover {
  background: #1d4ed8;
  transform: scale(1.1);
}

.budget-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #2563eb;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
}

.budget-slider::-moz-range-thumb:hover {
  background: #1d4ed8;
  transform: scale(1.1);
}

.budget-display {
  font-size: 2.5rem;
  font-weight: 700;
  color: #0f172a;
  text-align: center;
  letter-spacing: -0.025em;
}

.total-cost {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
  font-size: 0.938rem;
  color: #64748b;
}

.total-cost strong {
  color: #0f172a;
  font-size: 1.125rem;
}

.budget-remaining {
  color: #059669;
  font-size: 0.875rem;
}

.budget-exceeded {
  color: #dc2626;
  font-size: 0.875rem;
  font-weight: 600;
}

.no-items {
  text-align: center;
  padding: 2rem;
  color: #64748b;
  font-style: italic;
}

.action-section {
  padding: 1.25rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
}

.place-order-btn {
  padding: 0.75rem 1.5rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.938rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.place-order-btn:hover:not(:disabled) {
  background: #1d4ed8;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.place-order-btn:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
  transform: none;
}
</style>
