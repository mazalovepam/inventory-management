<template>
  <div class="low-stock-alerts">
    <div class="page-header">
      <h2>{{ t('alerts.title') }}</h2>
      <p>{{ t('alerts.subtitle') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <!-- Summary Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">{{ t('alerts.totalAlerts') }}</div>
          <div class="stat-value">{{ lowStockItems.length }}</div>
        </div>
        <div class="stat-card danger">
          <div class="stat-label">{{ t('alerts.criticalAlerts') }}</div>
          <div class="stat-value">{{ criticalCount }}</div>
          <div class="stat-subtitle">&gt; 30% below reorder</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">{{ t('alerts.warningAlerts') }}</div>
          <div class="stat-value">{{ warningCount }}</div>
          <div class="stat-subtitle">10-30% below reorder</div>
        </div>
      </div>

      <!-- No Alerts State -->
      <div v-if="lowStockItems.length === 0" class="no-alerts">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="success-icon">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <p class="no-alerts-text">{{ t('alerts.allStocked') }}</p>
      </div>

      <!-- Alerts Table -->
      <div v-else class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('alerts.alertsList') }} ({{ filteredItems.length }})</h3>
          <div class="search-box">
            <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              :placeholder="t('alerts.searchPlaceholder')"
              class="search-input"
            />
            <button
              v-if="searchQuery"
              @click="searchQuery = ''"
              class="clear-search"
              :title="t('inventory.clearSearch')"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>

        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th @click="sortBy('sku')" class="sortable">
                  {{ t('alerts.sku') }}
                  <span v-if="sortColumn === 'sku'" class="sort-indicator">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('name')" class="sortable">
                  {{ t('alerts.itemName') }}
                  <span v-if="sortColumn === 'name'" class="sort-indicator">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th>{{ t('alerts.category') }}</th>
                <th>{{ t('alerts.warehouse') }}</th>
                <th @click="sortBy('quantity_on_hand')" class="sortable">
                  {{ t('alerts.currentStock') }}
                  <span v-if="sortColumn === 'quantity_on_hand'" class="sort-indicator">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th>{{ t('alerts.reorderPoint') }}</th>
                <th @click="sortBy('shortage')" class="sortable">
                  {{ t('alerts.shortage') }}
                  <span v-if="sortColumn === 'shortage'" class="sort-indicator">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('shortage_percentage')" class="sortable">
                  {{ t('alerts.urgency') }}
                  <span v-if="sortColumn === 'shortage_percentage'" class="sort-indicator">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in sortedItems"
                :key="item.sku"
                class="clickable-row"
                @click="showItemDetail(item)"
              >
                <td><strong>{{ item.sku }}</strong></td>
                <td>{{ translateProductName(item.name) }}</td>
                <td>{{ translateCategory(item.category) }}</td>
                <td>{{ translateWarehouse(item.warehouse) }}</td>
                <td>
                  <strong :style="{ color: getStockColor(item) }">
                    {{ item.quantity_on_hand }}
                  </strong>
                </td>
                <td>{{ item.reorder_point }}</td>
                <td>
                  <span :class="['badge', getUrgencyBadgeClass(item)]">
                    {{ item.shortage }} units
                  </span>
                </td>
                <td>
                  <div class="urgency-cell">
                    <span :class="['badge', getUrgencyBadgeClass(item)]">
                      {{ getUrgencyLabel(item) }}
                    </span>
                    <div class="urgency-bar-container">
                      <div
                        class="urgency-bar"
                        :class="getUrgencyClass(item)"
                        :style="{ width: Math.min(item.shortage_percentage, 100) + '%' }"
                      ></div>
                    </div>
                    <span class="urgency-percentage">{{ item.shortage_percentage.toFixed(1) }}%</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <InventoryDetailModal
      :is-open="showItemModal"
      :inventory-item="selectedItem"
      @close="showItemModal = false"
    />
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import { api } from '../api'
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'
import InventoryDetailModal from '../components/InventoryDetailModal.vue'

export default {
  name: 'LowStockAlerts',
  components: {
    InventoryDetailModal
  },
  setup() {
    const { t, translateProductName, translateWarehouse } = useI18n()

    const loading = ref(true)
    const error = ref(null)
    const lowStockItems = ref([])
    const searchQuery = ref('')
    const sortColumn = ref('shortage_percentage')
    const sortDirection = ref('desc')

    // Modal state
    const showItemModal = ref(false)
    const selectedItem = ref(null)

    // Use shared filters
    const { selectedLocation, selectedCategory, getCurrentFilters } = useFilters()

    // Severity counts
    const criticalCount = computed(() =>
      lowStockItems.value.filter(i => i.shortage_percentage > 30).length
    )

    const warningCount = computed(() =>
      lowStockItems.value.filter(i => i.shortage_percentage > 10 && i.shortage_percentage <= 30).length
    )

    // Filter items by search query
    const filteredItems = computed(() => {
      let filtered = lowStockItems.value

      if (searchQuery.value.trim()) {
        const query = searchQuery.value.toLowerCase().trim()
        filtered = filtered.filter(item =>
          item.name.toLowerCase().includes(query) ||
          item.sku.toLowerCase().includes(query)
        )
      }

      return filtered
    })

    // Sort filtered items
    const sortedItems = computed(() => {
      const items = [...filteredItems.value]

      items.sort((a, b) => {
        let aVal = a[sortColumn.value]
        let bVal = b[sortColumn.value]

        // Handle string sorting
        if (typeof aVal === 'string') {
          aVal = aVal.toLowerCase()
          bVal = bVal.toLowerCase()
        }

        if (sortDirection.value === 'asc') {
          return aVal > bVal ? 1 : aVal < bVal ? -1 : 0
        } else {
          return aVal < bVal ? 1 : aVal > bVal ? -1 : 0
        }
      })

      return items
    })

    const loadLowStockItems = async () => {
      try {
        loading.value = true
        error.value = null
        const filters = getCurrentFilters()
        lowStockItems.value = await api.getLowStockItems({
          warehouse: filters.warehouse,
          category: filters.category
        })
      } catch (err) {
        error.value = 'Failed to load low stock items: ' + err.message
      } finally {
        loading.value = false
      }
    }

    // Watch for filter changes and reload data
    watch([selectedLocation, selectedCategory], () => {
      loadLowStockItems()
    })

    const sortBy = (column) => {
      if (sortColumn.value === column) {
        sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
      } else {
        sortColumn.value = column
        sortDirection.value = column === 'shortage_percentage' || column === 'shortage' ? 'desc' : 'asc'
      }
    }

    const translateCategory = (category) => {
      const categoryMap = {
        'Circuit Boards': t('categories.circuitBoards'),
        'Sensors': t('categories.sensors'),
        'Actuators': t('categories.actuators'),
        'Controllers': t('categories.controllers'),
        'Power Supplies': t('categories.powerSupplies')
      }
      return categoryMap[category] || category
    }

    const getUrgencyClass = (item) => {
      if (item.shortage_percentage > 30) return 'critical'
      if (item.shortage_percentage > 10) return 'warning'
      return 'low-urgency'
    }

    const getUrgencyBadgeClass = (item) => {
      if (item.shortage_percentage > 30) return 'danger'
      if (item.shortage_percentage > 10) return 'warning'
      return 'info'
    }

    const getUrgencyLabel = (item) => {
      if (item.shortage_percentage > 30) return 'Critical'
      if (item.shortage_percentage > 10) return 'Warning'
      return 'Low'
    }

    const getStockColor = (item) => {
      if (item.shortage_percentage > 30) return '#ef4444'
      if (item.shortage_percentage > 10) return '#f59e0b'
      return '#f97316'
    }

    const showItemDetail = (item) => {
      selectedItem.value = item
      showItemModal.value = true
    }

    onMounted(loadLowStockItems)

    return {
      t,
      loading,
      error,
      lowStockItems,
      searchQuery,
      sortColumn,
      sortDirection,
      filteredItems,
      sortedItems,
      criticalCount,
      warningCount,
      showItemModal,
      selectedItem,
      sortBy,
      translateCategory,
      translateProductName,
      translateWarehouse,
      getUrgencyClass,
      getUrgencyBadgeClass,
      getUrgencyLabel,
      getStockColor,
      showItemDetail,
      Math
    }
  }
}
</script>

<style scoped>
.page-header {
  margin-bottom: 1.5rem;
}

.page-header h2 {
  margin-bottom: 0.25rem;
}

.page-header p {
  color: #64748b;
  font-size: 0.875rem;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1.25rem;
}

.stat-card.danger {
  border-color: #fecaca;
  background: linear-gradient(135deg, #fef2f2 0%, #ffffff 100%);
}

.stat-card.warning {
  border-color: #fed7aa;
  background: linear-gradient(135deg, #fffbeb 0%, #ffffff 100%);
}

.stat-label {
  font-size: 0.813rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
}

.stat-subtitle {
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 0.25rem;
}

/* No Alerts State */
.no-alerts {
  padding: 3rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.success-icon {
  width: 48px;
  height: 48px;
  color: #10b981;
}

.no-alerts-text {
  font-size: 1.125rem;
  color: #10b981;
  font-weight: 600;
  margin: 0;
}

/* Card and Table */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1.5rem;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.card-title {
  font-size: 1rem;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  min-width: 300px;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  width: 18px;
  height: 18px;
  color: #94a3b8;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 0.5rem 2.5rem 0.5rem 2.5rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #0f172a;
  background: #f8fafc;
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  background: white;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-input::placeholder {
  color: #94a3b8;
}

.clear-search {
  position: absolute;
  right: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}

.clear-search:hover {
  background: #e2e8f0;
  color: #64748b;
}

.clear-search svg {
  width: 18px;
  height: 18px;
}

/* Table Styles */
.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  text-align: left;
  padding: 1rem 1.25rem;
  background: #f8fafc;
  border-top: 1px solid #f1f5f9;
  border-bottom: 1px solid #e2e8f0;
  color: #475569;
  font-weight: 600;
  font-size: 0.813rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

th.sortable {
  cursor: pointer;
  user-select: none;
  transition: background-color 0.15s ease;
}

th.sortable:hover {
  background: #f1f5f9;
}

.sort-indicator {
  margin-left: 0.25rem;
  font-size: 0.75rem;
  color: #3b82f6;
}

td {
  padding: 1rem 1.25rem;
  border-top: 1px solid #f1f5f9;
  color: #334155;
  font-size: 0.875rem;
}

tbody tr {
  transition: background-color 0.15s ease;
}

tbody tr:hover {
  background: #f8fafc;
}

.clickable-row {
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.clickable-row:hover {
  background: #eff6ff !important;
}

/* Urgency Cell */
.urgency-cell {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: flex-start;
  min-width: 180px;
}

.urgency-bar-container {
  width: 100%;
  height: 8px;
  background: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
}

.urgency-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.urgency-bar.critical {
  background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%);
}

.urgency-bar.warning {
  background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%);
}

.urgency-bar.low-urgency {
  background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
}

.urgency-percentage {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 600;
}

.loading,
.error {
  padding: 2rem;
  text-align: center;
  color: #64748b;
}

.error {
  color: #ef4444;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
}
</style>
