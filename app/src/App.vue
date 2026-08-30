<script setup>
import { ref } from 'vue'

const files = ref([])
const input = ref(null)
const supported = '.caproj,.plan,.layout,.pdf,.dxf,.dwg'
const apiBase = 'http://127.0.0.1:8000'
const analysis = ref(null)
const apiError = ref('')
const evidencePages = ref([])
const sourceUrl = ref('')
const decisions = ref({})

async function addFiles(selected) {
  for (const file of Array.from(selected)) {
    const entry = {
    id: `${file.name}-${file.lastModified}`,
    name: file.name,
    size: file.size,
    status: 'Uploading',
    }
    files.value.push(entry)
    const form = new FormData()
    form.append('file', file)
    try {
      const response = await fetch(`${apiBase}/projects/sweeter-build/files`, { method: 'POST', body: form })
      if (!response.ok) throw new Error(`Upload failed (${response.status})`)
      const stored = await response.json()
      entry.status = 'Complete'
      analysis.value = { status: 'Starting analysis…', snapshotId: stored.id }
      const runResponse = await fetch(`${apiBase}/projects/sweeter-build/runs?snapshot_id=${stored.id}`, { method: 'POST' })
      if (!runResponse.ok) throw new Error(`Analysis failed (${runResponse.status})`)
      analysis.value = await runResponse.json()
      evidencePages.value = analysis.value.result?.evidence || []
      if (file.type === 'application/pdf') sourceUrl.value = `${apiBase}/projects/sweeter-build/snapshots/${stored.id}/source`
    } catch (error) {
      entry.status = 'Failed'
      apiError.value = error.message
    }
  }
}

function removeFile(id) { files.value = files.value.filter((file) => file.id !== id) }
function decide(id, decision) { decisions.value = { ...decisions.value, [id]: decision } }
function formatSize(bytes) { return `${Math.max(1, Math.round(bytes / 1024))} KB` }
</script>

<template>
  <main class="min-h-screen bg-slate-100 text-slate-950">
    <header class="border-b border-slate-200 bg-white px-8 py-6">
      <div class="mx-auto flex max-w-6xl items-center justify-between">
        <div><div class="text-2xl font-bold">RES Works</div><div class="text-xs tracking-[0.35em] text-slate-400">RES PLAN / LOCAL REVIEW</div></div>
        <div class="text-sm text-slate-500"><span class="mr-2 text-emerald-500">●</span>Local workspace / Sweeter Build</div>
      </div>
    </header>
    <section class="mx-auto max-w-6xl space-y-8 px-8 py-12">
      <div><p class="text-xs font-bold tracking-[0.3em] text-slate-400">PROJECT WORKSPACE</p><h1 class="mt-3 text-5xl font-bold tracking-tight">Plan intake &amp; review</h1><p class="mt-4 max-w-3xl text-lg text-slate-500">Import Chief Architect exports, review evidence, and prepare controlled handoff actions. Geometry stays local and Chief remains authoritative.</p></div>
      <section class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
        <div class="flex items-start justify-between"><div><h2 class="text-2xl font-bold">1. Add source files</h2><p class="mt-2 text-slate-400">Chief exports, PDFs, CAD evidence, or project data</p></div><span class="text-2xl font-bold text-slate-200">01</span></div>
        <input ref="input" class="hidden" type="file" :accept="supported" multiple @change="addFiles($event.target.files)">
        <button class="mt-8 flex min-h-48 w-full flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-300 bg-slate-50 hover:border-orange-400 hover:bg-orange-50" @click="input.click()" @dragover.prevent @drop.prevent="addFiles($event.dataTransfer.files)">
          <span class="mb-4 rounded-full bg-orange-100 px-5 py-3 text-3xl text-orange-500">↑</span><span class="text-lg font-semibold">Drop files here or <span class="text-orange-500">browse</span></span><span class="mt-2 text-sm text-slate-400">CAPROJ, PLAN, LAYOUT, PDF, DXF, or DWG · local only</span>
        </button>
        <div v-if="files.length" class="mt-5 divide-y divide-slate-200 rounded-2xl border border-slate-200">
          <div v-for="file in files" :key="file.id" class="flex items-center gap-4 p-4"><div class="rounded-xl bg-slate-100 px-3 py-2 text-xs font-bold text-slate-500">{{ file.name.split('.').pop().toUpperCase() }}</div><div class="min-w-0 flex-1"><div class="truncate font-semibold">{{ file.name }}</div><div class="text-sm text-slate-400">{{ formatSize(file.size) }} · {{ file.status }}</div></div><button class="text-sm text-slate-400 hover:text-red-500" @click="removeFile(file.id)">Remove</button></div>
        </div>
      </section>
      <section class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm"><div class="flex justify-between"><div><h2 class="text-2xl font-bold">2. Review evidence</h2><p class="mt-2 text-slate-400">PDF pages, geometry findings, and documentation recommendations will appear here.</p></div><span class="text-2xl font-bold text-slate-200">02</span></div><div v-if="apiError" class="mt-6 rounded-xl bg-red-50 p-4 text-red-700">{{ apiError }}</div><div v-else-if="analysis" class="mt-8 rounded-2xl border border-emerald-200 bg-emerald-50 p-6"><div class="flex items-center justify-between"><span class="font-semibold">Analysis run</span><span class="font-bold text-emerald-700">{{ analysis.status }}</span></div><p v-if="analysis.result" class="mt-3 text-emerald-800">{{ analysis.result.message }} · {{ analysis.result.pages }} pages indexed</p><p v-if="analysis.result?.architectural_entity_count" class="mt-2 text-emerald-800">{{ analysis.result.architectural_entity_count }} architectural CAD entities extracted</p><p v-if="analysis.result?.fact_count" class="mt-2 text-emerald-800">{{ analysis.result.fact_count }} geometry facts · {{ analysis.result.geometry_errors?.length || 0 }} geometry errors · {{ analysis.result.recommendations?.length || 0 }} recommendations</p><div v-if="sourceUrl" class="mt-6 overflow-hidden rounded-xl border border-slate-200 bg-white"><iframe :src="sourceUrl" title="PDF source viewer" class="h-[560px] w-full"></iframe></div><div v-if="evidencePages.length" class="mt-6 space-y-3"><h3 class="font-semibold text-slate-700">Indexed pages</h3><div v-for="page in evidencePages" :key="page.page_number" class="rounded-xl border border-slate-200 bg-white p-4"><div class="font-semibold">Page {{ page.page_number }}</div><p class="mt-2 whitespace-pre-wrap text-sm text-slate-600">{{ page.text || 'No extractable text; visual review required.' }}</p></div></div><div v-if="analysis.result?.recommendations?.length" class="mt-6 space-y-3"><h3 class="font-semibold text-slate-700">Documentation recommendations</h3><div v-for="item in analysis.result.recommendations" :key="item.id" class="rounded-xl border border-orange-200 bg-white p-4"><div class="flex items-center justify-between"><div><div class="font-semibold">{{ item.documentation_item_id }}</div><p class="mt-1 text-sm text-slate-600">{{ item.reason }}</p></div><span class="text-xs font-bold uppercase text-slate-500">{{ decisions[item.id] || 'proposed' }}</span></div><div class="mt-4 flex gap-2"><button class="rounded-lg bg-emerald-600 px-3 py-2 text-xs font-semibold text-white" @click="decide(item.id, 'approved')">Approve</button><button class="rounded-lg bg-slate-200 px-3 py-2 text-xs font-semibold text-slate-700" @click="decide(item.id, 'deferred')">Defer</button><button class="rounded-lg bg-red-100 px-3 py-2 text-xs font-semibold text-red-700" @click="decide(item.id, 'rejected')">Reject</button></div></div><div class="mt-5 rounded-xl border border-slate-200 bg-white p-4"><div class="font-semibold">Chief handoff</div><p class="mt-1 text-sm text-slate-600">Only approved recommendations will be included in the supervised handoff.</p><div class="mt-3 text-sm text-slate-700">{{ Object.values(decisions).filter((decision) => decision === 'approved').length }} approved item(s) ready for review in Chief Architect.</div></div></div></div><div v-else class="mt-8 flex min-h-40 items-center justify-center rounded-2xl border-2 border-dashed border-slate-200 text-slate-400">Upload a source file to start an analysis run</div></section>
    </section>
  </main>
</template>
