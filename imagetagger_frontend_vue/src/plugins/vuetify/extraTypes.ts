import Vue from 'vue'

// Custom type definitions for vuetify component instances that expose extra functions or properties but are not
// part of default vuetify definitions

/**
 * Custom interface definition of v-form instances
 */
export interface VFormType extends Vue {
    validate(): boolean
    reset(): void
    resetErrorBag(): void
    resetValidation(): void
}
