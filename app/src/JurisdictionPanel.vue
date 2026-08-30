<script setup>
import { computed, onMounted, ref } from 'vue'

const emit = defineEmits(['change'])

const apiBase = 'http://127.0.0.1:8000'
const profiles = ref([])
const selected = ref('arkansas-baseline')
const selectedProfile = computed(() => profiles.value.find((profile) => profile.id === selected.value))

onMounted(async () => {
  const response = await fetch(`${apiBase}/jurisdictions`)
  if (response.ok) profiles.value = await response.json()
})
</script>

<template>
  <section class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
    <div class="flex items-start justify-between">
      <div><h2 class="text-2xl font-bold">Review jurisdiction</h2><p class="mt-2 text-slate-400">Select the governing profile before interpreting validation results.</p></div>
      <span class="text-2xl font-bold text-slate-200">J</span>
    </div>
    <select v-model="selected" @change="emit('change', selected)" class="mt-6 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-slate-700" aria-label="Review jurisdiction">
      <option v-for="profile in profiles" :key="profile.id" :value="profile.id">{{ profile.jurisdiction }}</option>
    </select>
    <div v-if="selectedProfile" class="mt-4 rounded-xl bg-amber-50 p-4 text-sm text-amber-900">
      <span class="font-semibold">{{ selectedProfile.building_code }}</span> · {{ selectedProfile.status.replaceAll('_', ' ') }}
      <p class="mt-1">Confirm the applicable AHJ and local amendments before relying on results.</p>
    </div>
  </section>
</template>
