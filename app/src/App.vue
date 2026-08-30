<script setup>
import { computed, onMounted, ref } from 'vue'
import JurisdictionPanel from './JurisdictionPanel.vue'

const files = ref([])
const input = ref(null)
const supported = '.caproj,.plan,.layout,.pdf,.dxf,.dwg'
const apiBase = 'http://127.0.0.1:8000'
const analysis = ref(null)
const apiError = ref('')
const evidencePages = ref([])
const sourceUrl = ref('')
const decisions = ref({})
const selectedJurisdiction = ref('arkansas-baseline')
const companionChecklist = computed(() => {
  const coverage = analysis.value?.result?.evidence_coverage
  if (!coverage) return []
  const labels = { geometry: ['Geometry export', 'Export All Floors (DXF/DWG)'], visual: ['Verification PDF', 'Export PDF'], schedules: ['Schedules', 'PDF or schedule export'], energy: ['Energy evidence', 'Thermal Envelope Data or RESCheck'] }
  return Object.entries(coverage).map(([kind, item]) => ({ kind, ...(labels[kind] || [kind, 'Chief export']), ...item }))
})
const reviewSummary = computed(() => {
  const result = analysis.value?.result
  if (!result) return null
  const coverage = result.evidence_coverage || {}
  const findings = result.bundle_analysis?.findings || []
  const recommendations = result.recommendations || []
  const missing = Object.entries(coverage).filter(([, item]) => item.status === 'missing').map(([kind]) => kind)
  const errors = result.geometry_errors?.length || 0
  let nextAction = 'Review the extracted evidence and confirm the plan in Chief Architect.'
  if (analysis.value.status === 'failed') nextAction = 'Retry analysis or correct the source export.'
  else if (missing.length) nextAction = `Add missing evidence: ${missing.join(', ')}.`
  else if (findings.length || errors) nextAction = 'Resolve the findings below, then export a fresh verification PDF.'
  else if (recommendations.length) nextAction = 'Review and approve the recommended documentation changes.'
  return { missing, findings: findings.length, errors, recommendations: recommendations.length, nextAction }
})

async function loadLatestAnalysis() {
  const response = await fetch(`${apiBase}/projects/sweeter-build/runs`)
  if (!response.ok) return
  const runs = await response.json()
  if (!runs.length) return
  analysis.value = runs[runs.length - 1]
  evidencePages.value = analysis.value.result?.evidence || []
  const bundle = analysis.value.result?.evidence_bundle || []
  files.value = bundle.map((item) => ({ id: item.snapshot_id, snapshotId: item.snapshot_id, name: item.filename, size: item.byte_size, status: 'Complete' }))
  const pdf = analysis.value.result?.bundle_analysis?.pdf?.[0]
  if (pdf) sourceUrl.value = `${apiBase}/projects/sweeter-build/snapshots/${pdf.snapshot_id}/source`
  else if (evidencePages.value.length) sourceUrl.value = `${apiBase}/projects/sweeter-build/snapshots/${analysis.value.source_snapshot_ids[0]}/source`
}

onMounted(loadLatestAnalysis)

async function addFiles(selected) {
  const selectedFiles = Array.from(selected)
  const uploaded = []
  apiError.value = ''
  analysis.value = { status: 'Uploading source bundle…' }
  for (const file of selectedFiles) {
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
      if (!response.ok) throw new Error(`Upload failed (${response.status}): ${await response.text()}`)
      const stored = await response.json()
      entry.snapshotId = stored.id
      entry.status = 'Complete'
      uploaded.push({ file, stored })
    } catch (error) {
      entry.status = 'Failed'
      apiError.value = error.message || 'The local API could not complete the request.'
    }
  }
  const lastUpload = uploaded.at(-1)
  if (!lastUpload) { analysis.value = null; return }
  analysis.value = { status: 'Starting analysis…', snapshotId: lastUpload.stored.id }
  const runResponse = await fetch(`${apiBase}/projects/sweeter-build/runs?snapshot_id=${lastUpload.stored.id}&profile_id=${selectedJurisdiction.value}`, { method: 'POST' })
  if (!runResponse.ok) {
    analysis.value = { status: 'failed' }
    apiError.value = `Analysis failed (${runResponse.status}): ${await runResponse.text()}`
    return
  }
  analysis.value = { ...await runResponse.json(), snapshotId: lastUpload.stored.id }
  if (analysis.value.status === 'failed') apiError.value = analysis.value.result?.message || 'Analysis failed.'
  evidencePages.value = analysis.value.result?.evidence || []
  const pdfUpload = uploaded.find(({ file }) => file.type === 'application/pdf')
  if (pdfUpload) sourceUrl.value = `${apiBase}/projects/sweeter-build/snapshots/${pdfUpload.stored.id}/source`
}

async function removeFile(file) {
  if (file.snapshotId) {
    await fetch(`${apiBase}/projects/sweeter-build/snapshots/${file.snapshotId}`, { method: 'DELETE' })
  }
  files.value = files.value.filter((item) => item.id !== file.id)
  await loadLatestAnalysis()
}
async function clearEvidence() {
  await fetch(`${apiBase}/projects/sweeter-build/snapshots`, { method: 'DELETE' })
  files.value = []
  analysis.value = null
  evidencePages.value = []
  sourceUrl.value = ''
  apiError.value = ''
}
async function retryAnalysis() {
  if (!analysis.value?.snapshotId) return
  apiError.value = ''
  analysis.value = { status: 'Starting analysis…', snapshotId: analysis.value.snapshotId }
  const response = await fetch(`${apiBase}/projects/sweeter-build/runs?snapshot_id=${analysis.value.snapshotId}&profile_id=${selectedJurisdiction.value}`, { method: 'POST' })
  if (!response.ok) {
    apiError.value = `Analysis failed (${response.status}): ${await response.text()}`
    analysis.value = { status: 'failed', snapshotId: analysis.value.snapshotId }
    return
  }
  analysis.value = await response.json()
  evidencePages.value = analysis.value.result?.evidence || []
}
async function decide(id, decision) {
  const response = await fetch(`${apiBase}/projects/sweeter-build/recommendations/${id}/decision`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ recommendation_id: id, decision: decision === 'approved' ? 'approve' : decision === 'deferred' ? 'defer' : 'reject', decided_by: 'designer' }) })
  if (!response.ok) { apiError.value = `Could not save decision (${response.status})`; return }
  decisions.value = { ...decisions.value, [id]: decision }
}
function downloadHandoff() {
  if (analysis.value?.id) window.open(`${apiBase}/projects/sweeter-build/runs/${analysis.value.id}/handoff`, '_blank')
}
async function createCheckpoint() {
  if (!analysis.value?.id) return
  const response = await fetch(`${apiBase}/projects/sweeter-build/runs/${analysis.value.id}/checkpoints`, { method: 'POST' })
  if (!response.ok) { apiError.value = `Could not create checkpoint (${response.status})`; return }
  const checkpoint = await response.json()
  apiError.value = `Checkpoint ready: ${checkpoint.id}`
}
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
      <JurisdictionPanel @change="selectedJurisdiction = $event" />
      <section v-if="companionChecklist.length" aria-label="Companion evidence checklist" class="rounded-3xl border border-amber-200 bg-amber-50 p-8 shadow-sm">
        <div class="flex items-start justify-between"><div><h2 class="text-2xl font-bold text-amber-950">Companion evidence checklist</h2><p class="mt-2 text-amber-900">These exports determine what RES can verify. Missing evidence is not a code failure.</p></div><span class="text-2xl font-bold text-amber-300">01A</span></div>
        <div class="mt-5 grid gap-3 md:grid-cols-2"><div v-for="item in companionChecklist" :key="item.kind" class="rounded-xl bg-white p-4"><div class="flex items-center justify-between"><span class="font-semibold text-slate-800">{{ item[0] }}</span><span class="text-xs font-bold uppercase" :class="item.status === 'available' ? 'text-emerald-700' : 'text-amber-700'">{{ item.status }}</span></div><p class="mt-1 text-sm text-slate-500">{{ item[1] }}</p><p v-if="item.sources?.length" class="mt-2 text-xs text-slate-500">{{ item.sources.join(', ') }}</p></div></div>
      </section>
      <section v-if="reviewSummary" aria-label="Review summary" class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
        <div class="flex items-start justify-between"><div><h2 class="text-2xl font-bold">What needs attention</h2><p class="mt-2 text-slate-500">A decision-oriented summary of this analysis run.</p></div><span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold uppercase tracking-wide text-slate-500">Next action</span></div>
        <p class="mt-5 rounded-xl bg-orange-50 p-4 font-semibold text-orange-900">{{ reviewSummary.nextAction }}</p>
        <div class="mt-5 grid gap-3 sm:grid-cols-3"><div class="rounded-xl bg-slate-50 p-4"><div class="text-2xl font-bold text-slate-900">{{ reviewSummary.findings + reviewSummary.errors }}</div><div class="text-sm text-slate-500">Findings to review</div></div><div class="rounded-xl bg-slate-50 p-4"><div class="text-2xl font-bold text-slate-900">{{ reviewSummary.recommendations }}</div><div class="text-sm text-slate-500">Documentation actions</div></div><div class="rounded-xl bg-slate-50 p-4"><div class="text-2xl font-bold text-slate-900">{{ reviewSummary.missing.length }}</div><div class="text-sm text-slate-500">Evidence types missing</div></div></div>
      </section>
      <section class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
        <div class="flex items-start justify-between"><div><h2 class="text-2xl font-bold">1. Add source files</h2><p class="mt-2 text-slate-400">Chief exports, PDFs, CAD evidence, or project data</p></div><span class="text-2xl font-bold text-slate-200">01</span></div>
        <input ref="input" class="hidden" type="file" :accept="supported" multiple @change="addFiles($event.target.files)">
        <button class="mt-8 flex min-h-48 w-full flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-300 bg-slate-50 hover:border-orange-400 hover:bg-orange-50" @click="input.click()" @dragover.prevent @drop.prevent="addFiles($event.dataTransfer.files)">
          <span class="mb-4 rounded-full bg-orange-100 px-5 py-3 text-3xl text-orange-500">↑</span><span class="text-lg font-semibold">Drop files here or <span class="text-orange-500">browse</span></span><span class="mt-2 text-sm text-slate-400">CAPROJ, PLAN, LAYOUT, PDF, DXF, or DWG · local only</span>
        </button>
      <div v-if="files.length" class="mt-5 divide-y divide-slate-200 rounded-2xl border border-slate-200">
          <div v-for="file in files" :key="file.id" class="flex items-center gap-4 p-4"><div class="rounded-xl bg-slate-100 px-3 py-2 text-xs font-bold text-slate-500">{{ file.name.split('.').pop().toUpperCase() }}</div><div class="min-w-0 flex-1"><div class="truncate font-semibold">{{ file.name }}</div><div class="text-sm text-slate-400">{{ formatSize(file.size) }} · {{ file.status }}</div></div><button class="text-sm text-slate-400 hover:text-red-500" @click="removeFile(file)">Remove</button></div>
        </div>
        <button v-if="files.some((file) => file.snapshotId)" class="mt-4 text-sm font-semibold text-red-600" @click="clearEvidence">Clear project evidence</button>
      </section>
      <section class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm"><div class="flex justify-between"><div><h2 class="text-2xl font-bold">2. Review evidence</h2><p class="mt-2 text-slate-400">PDF pages, geometry findings, and documentation recommendations will appear here.</p></div><span class="text-2xl font-bold text-slate-200">02</span></div><div v-if="apiError" class="mt-6 rounded-xl bg-red-50 p-4 text-red-700"><div>{{ apiError }}</div><button v-if="analysis?.snapshotId" class="mt-3 rounded-lg bg-red-700 px-3 py-2 text-xs font-semibold text-white" @click="retryAnalysis">Retry analysis</button></div><div v-else-if="analysis" class="mt-8 rounded-2xl border border-emerald-200 bg-emerald-50 p-6"><div class="flex items-center justify-between"><span class="font-semibold">Analysis run</span><span class="font-bold text-emerald-700">{{ analysis.status }}</span></div><p v-if="analysis.result" class="mt-3 text-emerald-800">{{ analysis.result.message }} · {{ analysis.result.pages }} pages indexed</p><p v-if="analysis.result?.architectural_entity_count" class="mt-2 text-emerald-800">{{ analysis.result.architectural_entity_count }} architectural CAD entities extracted</p><p v-if="analysis.result?.fact_count" class="mt-2 text-emerald-800">{{ analysis.result.fact_count }} geometry facts · {{ analysis.result.geometry_errors?.length || 0 }} geometry errors · {{ analysis.result.recommendations?.length || 0 }} recommendations</p><div v-if="sourceUrl" class="mt-6 overflow-hidden rounded-xl border border-slate-200 bg-white"><iframe :src="sourceUrl" title="PDF source viewer" class="h-[560px] w-full"></iframe></div><div v-if="evidencePages.length" class="mt-6 space-y-3"><h3 class="font-semibold text-slate-700">Indexed pages</h3><div v-for="page in evidencePages" :key="page.page_number" class="rounded-xl border border-slate-200 bg-white p-4"><div class="font-semibold">Page {{ page.page_number }}</div><p class="mt-2 whitespace-pre-wrap text-sm text-slate-600">{{ page.text || 'No extractable text; visual review required.' }}</p></div></div><div v-if="analysis.result?.recommendations?.length" class="mt-6 space-y-3"><h3 class="font-semibold text-slate-700">Documentation recommendations</h3><div v-for="item in analysis.result.recommendations" :key="item.id" class="rounded-xl border border-orange-200 bg-white p-4"><div class="flex items-center justify-between"><div><div class="font-semibold">{{ item.documentation_item_id }}</div><p class="mt-1 text-sm text-slate-600">{{ item.reason }}</p></div><span class="text-xs font-bold uppercase text-slate-500">{{ decisions[item.id] || 'proposed' }}</span></div><div class="mt-4 flex gap-2"><button class="rounded-lg bg-emerald-600 px-3 py-2 text-xs font-semibold text-white" @click="decide(item.id, 'approved')">Approve</button><button class="rounded-lg bg-slate-200 px-3 py-2 text-xs font-semibold text-slate-700" @click="decide(item.id, 'deferred')">Defer</button><button class="rounded-lg bg-red-100 px-3 py-2 text-xs font-semibold text-red-700" @click="decide(item.id, 'rejected')">Reject</button></div></div><div class="mt-5 rounded-xl border border-slate-200 bg-white p-4"><div class="font-semibold">Chief handoff</div><p class="mt-1 text-sm text-slate-600">Only approved recommendations will be included in the supervised handoff.</p><div class="mt-3 text-sm text-slate-700">{{ Object.values(decisions).filter((decision) => decision === 'approved').length }} approved item(s) ready for review in Chief Architect.</div></div></div></div><div v-else class="mt-8 flex min-h-40 items-center justify-center rounded-2xl border-2 border-dashed border-slate-200 text-slate-400">Upload a source file to start an analysis run</div></section>
      <div v-if="analysis?.result?.native_files" class="mt-6 rounded-xl border border-slate-200 bg-white p-4"><h3 class="font-semibold text-slate-700">Native Chief artifacts</h3><div v-for="(files, kind) in analysis.result.native_files" :key="kind" class="mt-3"><div class="text-xs font-bold uppercase tracking-wide text-slate-400">{{ kind }}</div><div v-for="file in files" :key="file.archive_path" class="mt-2 flex justify-between rounded-lg bg-slate-50 px-3 py-2 text-sm"><span class="truncate">{{ file.archive_path }}</span><span class="ml-4 shrink-0 text-slate-500">{{ Math.round(file.byte_size / 1024) }} KB</span></div></div></div>
      <div v-if="analysis?.result?.evidence_bundle?.length" class="mt-6 rounded-xl border border-slate-200 bg-white p-4"><h3 class="font-semibold text-slate-700">Project evidence bundle</h3><p class="mt-1 text-sm text-slate-500">Sources currently associated with this project.</p><div v-for="item in analysis.result.evidence_bundle" :key="item.snapshot_id" class="mt-2 flex justify-between rounded-lg bg-slate-50 px-3 py-2 text-sm"><span>{{ item.filename }}</span><span class="text-slate-500">{{ Math.round(item.byte_size / 1024) }} KB</span></div></div>
      <div v-if="analysis?.result?.bundle_analysis" class="mt-6 rounded-xl border border-slate-200 bg-white p-4"><h3 class="font-semibold text-slate-700">Extracted evidence</h3><div class="mt-3 grid gap-3 md:grid-cols-2"><div class="rounded-lg bg-slate-50 p-3"><div class="font-semibold">CAD geometry</div><div class="text-sm text-slate-500">{{ analysis.result.bundle_analysis.geometry.length }} CAD source(s) found</div><div v-for="item in analysis.result.bundle_analysis.geometry" :key="item.snapshot_id" class="mt-2 text-xs text-slate-600"><div>{{ item.filename }} · {{ item.status === 'present_not_parsed' ? 'present; not parsed' : item.evidence_summary.entity_count + ' architectural entities' }}</div><div v-if="item.evidence_summary.categories" class="mt-2 flex flex-wrap gap-1"><span v-for="(count, category) in item.evidence_summary.categories" :key="category" class="rounded bg-white px-2 py-1">{{ category }}: {{ count }}</span></div><div v-if="item.evidence_summary.inventory?.dimension_count" class="mt-2">Dimensions: {{ item.evidence_summary.inventory.dimension_count }}</div><div v-if="item.evidence_summary.text_samples?.room_labels?.length" class="mt-2">Room labels: {{ item.evidence_summary.text_samples.room_labels.slice(0, 5).join(', ') }}</div></div></div><div class="rounded-lg bg-slate-50 p-3"><div class="font-semibold">PDF evidence</div><div class="text-sm text-slate-500">{{ analysis.result.bundle_analysis.pdf.length }} PDF source(s) indexed</div><div v-for="item in analysis.result.bundle_analysis.pdf" :key="item.snapshot_id" class="mt-1 text-xs text-slate-600">{{ item.filename }} · {{ item.pages }} page(s)</div></div></div><p class="mt-3 text-xs text-slate-500">{{ analysis.result.bundle_analysis.note }}</p></div>
      <div v-if="analysis?.result?.bundle_analysis?.findings?.length" class="mt-6 rounded-xl border border-orange-200 bg-orange-50 p-4"><h3 class="font-semibold text-orange-900">Review findings</h3><div v-for="finding in analysis.result.bundle_analysis.findings" :key="finding.message + finding.source_snapshot_id" class="mt-2 rounded-lg bg-white p-3 text-sm text-slate-700"><span class="mr-2 text-xs font-bold uppercase text-orange-700">{{ finding.severity }}</span>{{ finding.message }}<span v-if="finding.source_filename" class="mt-1 block text-xs text-slate-500">Source: {{ finding.source_filename }}</span></div></div>
      <div v-if="analysis?.result?.evidence_coverage" class="mt-6 rounded-xl border border-amber-200 bg-amber-50 p-4"><h3 class="font-semibold text-amber-900">Analysis coverage</h3><p class="mt-1 text-sm text-amber-800">Evidence is tracked by type. Available files are ready for processing; missing types are called out explicitly.</p><div class="mt-3 grid gap-2 md:grid-cols-2"><div v-for="(item, kind) in analysis.result.evidence_coverage" :key="kind" class="rounded-lg bg-white p-3"><div class="flex justify-between"><div class="font-semibold capitalize text-slate-700">{{ kind }}</div><div class="text-xs font-bold uppercase" :class="item.status === 'available' ? 'text-emerald-700' : 'text-amber-700'">{{ item.status }}</div></div><div v-if="item.sources.length" class="mt-1 text-xs text-slate-500">{{ item.sources.join(', ') }}</div></div></div></div>
      <section v-if="analysis?.result?.bundle_analysis?.dimension_comparison" class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm"><h2 class="text-xl font-bold">Dimension comparison</h2><p class="mt-2 text-slate-500">{{ analysis.result.bundle_analysis.dimension_comparison.source_count }} DXF source(s) compared · {{ analysis.result.bundle_analysis.dimension_comparison.matched_source_count }} source(s) matched</p><div v-if="analysis.result.bundle_analysis.dimension_comparison.finding_count" class="mt-4 space-y-2"><div v-for="finding in analysis.result.bundle_analysis.dimension_comparison.findings" :key="finding" class="rounded-lg bg-amber-50 p-3 text-sm text-amber-800">{{ finding }}</div></div><div v-else class="mt-4 text-sm text-emerald-700">Repeated normalized dimensions found: {{ Object.keys(analysis.result.bundle_analysis.dimension_comparison.repeated_dimensions).length }}</div><div v-for="(items, value) in analysis.result.bundle_analysis.dimension_comparison.repeated_dimensions" :key="value" class="mt-3 rounded-lg bg-slate-50 p-3 text-sm"><span class="font-semibold">{{ value }}</span><span class="ml-2 text-slate-500">{{ items.map((item) => `${item.filename} (${item.handle || 'no handle'})`).join(' · ') }}</span></div></section>
      <section v-if="analysis?.result?.bundle_analysis?.geometry?.some((item) => item.preview_url)" class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm"><h2 class="text-xl font-bold">CAD preview</h2><p class="mt-2 text-slate-500">Local SVG preview of parsed DXF linework and labels. Chief remains authoritative.</p><div v-for="item in analysis.result.bundle_analysis.geometry.filter((entry) => entry.preview_url)" :key="item.snapshot_id" class="mt-5"><div class="mb-2 font-semibold">{{ item.filename }}</div><img :src="`http://127.0.0.1:8000${item.preview_url}`" :alt="`${item.filename} SVG preview`" class="max-h-[700px] w-full rounded-xl border border-slate-200 bg-white object-contain" /></div></section>
      <section v-if="analysis?.result?.recommendations?.length" class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm"><h2 class="text-xl font-bold">Recommended documentation</h2><p class="mt-2 text-slate-500">Review these proposed notes and callouts before applying anything in Chief Architect.</p><div v-for="item in analysis.result.recommendations" :key="item.id" class="mt-4 rounded-xl border border-orange-200 bg-orange-50 p-4"><div class="flex items-center justify-between"><div class="font-semibold">{{ item.title }}</div><span class="text-xs font-bold uppercase text-slate-500">{{ decisions[item.id] || item.status }}</span></div><p class="mt-2 text-sm text-slate-700">{{ item.proposed_text }}</p><p class="mt-2 text-xs text-slate-500">{{ item.category }} · Target: {{ item.target_sheet }} · Confidence: {{ item.confidence }}<span v-if="item.professional_review_required"> · Professional review required</span></p><p v-if="item.source_refs?.length" class="mt-1 text-xs text-slate-500">Evidence: {{ item.source_refs.join(', ') }}</p></div></section>
      <section v-if="analysis?.id" class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm"><h2 class="text-xl font-bold">Chief handoff safety</h2><p class="mt-2 text-sm text-slate-600">Approved items can be downloaded as an editable checklist. Create a checkpoint before editing Chief.</p><div class="mt-4 flex gap-2"><button class="rounded-lg bg-slate-900 px-3 py-2 text-xs font-semibold text-white" @click="downloadHandoff">Download Chief handoff</button><button class="rounded-lg bg-slate-200 px-3 py-2 text-xs font-semibold text-slate-700" @click="createCheckpoint">Create checkpoint</button></div></section>
      <section v-if="analysis?.result?.bundle_analysis?.geometry?.some((item) => item.preview_url)" class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm"><h2 class="text-xl font-bold">Floor 1 SVG output</h2><p class="mt-2 text-sm text-slate-600">Architectural layers and dimensions are fitted to the Floor 1 plan view. Download the SVG for review or import into a graphics/CAD tool.</p><div v-for="item in analysis.result.bundle_analysis.geometry.filter((entry) => entry.preview_url)" :key="`download-${item.snapshot_id}`" class="mt-3"><a class="font-semibold text-blue-700 underline" :href="`${apiBase}${item.preview_url}`" download>{{ item.filename.replace(/\.dxf$/i, '.svg') }}</a></div></section>
    </section>
  </main>
</template>
