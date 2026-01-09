import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:5173';

test('User can submit a valid order', async ({ page }) => {
  await page.goto(BASE_URL);

  // 1. Definitive Readiness Check: Wait directly for the first form element to be visible.
  // This is the most robust way to ensure the component has rendered.
  await expect(page.getByTestId('order-form-symbol')).toBeVisible({ timeout: 20000 });

  // 2. Fill out the order form
  await page.getByTestId('order-form-symbol').fill('SPY');
  await page.getByTestId('order-form-qty').fill('10');
  await page.getByTestId('order-form-price').fill('450.00');

  // 3. Submit
  await page.getByTestId('order-form-submit-btn').click();

  // 4. Verify Success Message
  await expect(page.getByTestId('order-form-status')).toContainText('SUCCESS: SUBMITTED');
});

test('User sees error for oversized order', async ({ page }) => {
  await page.goto(BASE_URL);

  // 1. Definitive Readiness Check
  await expect(page.getByTestId('order-form-symbol')).toBeVisible({ timeout: 20000 });

  // 2. Fill out an oversized order
  await page.getByTestId('order-form-symbol').fill('SPY');
  await page.getByTestId('order-form-qty').fill('1000'); 
  await page.getByTestId('order-form-price').fill('450.00');

  // 3. Submit
  await page.getByTestId('order-form-submit-btn').click();

  // 4. Verify Error Message
  await expect(page.getByTestId('order-form-status')).toContainText('ERROR: REJECT: Order value');
});
