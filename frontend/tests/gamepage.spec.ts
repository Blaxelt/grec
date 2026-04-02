import { test, expect } from '@playwright/test';

test.describe('Gamepage', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/games/570940');
  });

  test('has title', async ({ page }) => {
    await expect(page).toHaveTitle("Grec");
  });

  test('has correct game name', async ({ page }) => {
    await expect(page.getByRole('heading', { level: 1, name: /dark souls/i })).toBeVisible();
  });

  test('has game description', async ({ page }) => {
    await expect(page.locator('.game-description')).toBeVisible();
  });

  test('has game genres', async ({ page }) => {
    await expect(page.getByText(/Genres:/)).toBeVisible();
  });
  test('has game tags', async ({ page }) => {
    await expect(page.getByText(/Tags:/)).toBeVisible();
  });

  test('shows error for invalid game', async ({ page }) => {
    await page.goto('/games/99999999');
    await expect(page.getByText('Loading...')).toBeVisible();
  });
});
