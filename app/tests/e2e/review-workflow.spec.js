import { test, expect } from '@playwright/test'

test('upload remains visible and transitions through analysis into review', async ({ page }) => {
  await page.route('http://127.0.0.1:8000/projects/sweeter-build/runs**', async (route) => {
    if (route.request().method() === 'GET') return route.fulfill({ json: [] })
    await route.fulfill({ json: { id: 'run-test', status: 'completed', result: { message: 'PDF pages indexed for review', pages: 2, evidence: [{ page_number: 1, text: 'Cover sheet' }, { page_number: 2, text: 'Floor plan' }] } } })
  })
  await page.route('http://127.0.0.1:8000/projects/sweeter-build/files**', async (route) => {
    await route.fulfill({ json: { id: 'snapshot-test', filename: 'plan.pdf', byte_size: 4, status: 'stored' } })
  })
  await page.goto('/')
  const chooser = page.waitForEvent('filechooser')
  await page.getByRole('button', { name: /drop files here or browse/i }).click()
  await (await chooser).setFiles({ name: 'plan.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF') })
  await expect(page.getByText('plan.pdf')).toBeVisible()
  await expect(page.getByText(/Complete/)).toBeVisible()
  await expect(page.getByText('PDF pages indexed for review')).toBeVisible()
  await expect(page.getByText(/2 pages indexed/)).toBeVisible()
  await expect(page.getByText('Page 1')).toBeVisible()
  await expect(page.getByText('Floor plan')).toBeVisible()
})

test('empty project clearly explains how to begin', async ({ page }) => {
  await page.route('http://127.0.0.1:8000/projects/sweeter-build/runs**', (route) => route.fulfill({ json: [] }))
  await page.goto('/')
  await expect(page.getByText('Upload a source file to start an analysis run')).toBeVisible()
})

test('jurisdiction selector shows conservative profile status', async ({ page }) => {
  await page.route('http://127.0.0.1:8000/projects/sweeter-build/runs**', (route) => route.fulfill({ json: [] }))
  await page.route('http://127.0.0.1:8000/jurisdictions', (route) => route.fulfill({ json: [
    { id: 'benton-bentonville-overlay', jurisdiction: 'Bentonville, Benton County', building_code: '2021 Arkansas Fire Prevention Code', status: 'needs_ahj_confirmation' },
  ] }))
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Review jurisdiction' })).toBeVisible()
  await expect(page.getByRole('option', { name: 'Bentonville, Benton County' })).toHaveCount(1)
  await page.getByRole('combobox', { name: 'Review jurisdiction' }).selectOption('benton-bentonville-overlay')
  await expect(page.getByText(/needs ahj confirmation/)).toBeVisible()
})

test('clear project evidence resets the upload state', async ({ page }) => {
  await page.route('http://127.0.0.1:8000/projects/sweeter-build/runs**', async (route) => {
    if (route.request().method() === 'GET') return route.fulfill({ json: [] })
    await route.fulfill({ json: { id: 'run-test', status: 'completed', result: { message: 'Indexed', pages: 0 } } })
  })
  await page.route('http://127.0.0.1:8000/projects/sweeter-build/files**', (route) => route.fulfill({ json: { id: 'snapshot-test', filename: 'plan.pdf', byte_size: 4, status: 'stored' } }))
  await page.route('http://127.0.0.1:8000/projects/sweeter-build/snapshots', (route) => route.fulfill({ json: { status: 'cleared', deleted: 1 } }))
  await page.goto('/')
  const chooser = page.waitForEvent('filechooser')
  await page.getByRole('button', { name: /drop files here or browse/i }).click()
  await (await chooser).setFiles({ name: 'plan.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF') })
  await expect(page.getByText('Clear project evidence')).toBeVisible()
  await page.getByText('Clear project evidence').click()
  await expect(page.getByText('Upload a source file to start an analysis run')).toBeVisible()
})
