import { test, expect } from '@playwright/test';

test.describe('Search Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/search');
  });

  test('has title', async ({ page }) => {
    await expect(page).toHaveTitle("Grec");
  });

  test('has heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Game details' })).toBeVisible();
  });

  test('has search bar', async ({ page }) => {
    await expect(page.getByPlaceholder('Search for a game...')).toBeVisible();
  });

  test('search bar empty at start', async ({ page }) => {
    await expect(page.getByPlaceholder('Search for a game...')).toBeEmpty();
  });

  test('search bar not empty after typing', async ({ page }) => {
    await page.getByPlaceholder('Search for a game...').fill('Game');

    await expect(page.getByPlaceholder('Search for a game...')).not.toBeEmpty();
  });

  test('search game', async ({ page }) => {
    await page.getByPlaceholder('Search for a game...').fill('ELDEN RING');
    await expect(page.getByTestId('suggestions')).toBeVisible();
    await page.getByRole('listitem').first().click();

    await expect(page).toHaveURL('/games/1245620');
  })
});