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
