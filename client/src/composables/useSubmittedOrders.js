import { ref } from 'vue'

// Shared state for submitted restocking orders (in-memory)
const submittedOrders = ref([])

export function useSubmittedOrders() {
  const submitRestockingOrder = (order) => {
    submittedOrders.value.unshift(order)
  }

  return {
    submittedOrders,
    submitRestockingOrder
  }
}
