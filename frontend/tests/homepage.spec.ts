import { test, expect } from '@playwright/test';

test.describe('Homepage', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('has title', async ({ page }) => {
    await expect(page).toHaveTitle("Grec");
  });

  test('has heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Grec' })).toBeVisible();
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

  test('similar results', async ({ page }) => {
    await page.getByPlaceholder('Search for a game...').fill('ELDEN RING');
    await expect(page.getByTestId('suggestions')).toBeVisible();
    await page.getByRole('listitem').first().click();

    await expect(page.getByTestId('results-list')).toBeVisible();
    const cards = page.getByTestId('results-list').getByTestId('result-card');
    await expect(cards).toHaveCount(10)
  })

  test('has filter button', async ({ page }) => {
    await expect(page.getByRole('button', { name: '⚙' })).toBeVisible();
  });

  test('filter changes result count', async ({ page }) => {
    await page.getByPlaceholder('Search for a game...').fill('ELDEN RING');
    await expect(page.getByTestId('suggestions')).toBeVisible();
    await page.getByRole('listitem').first().click();
    await expect(page.getByTestId('results-list')).toBeVisible();

    await page.getByRole('button', { name: '⚙' }).click();
    const slider = page.getByLabel('Number of recommendations');
    await slider.focus();
    for (let i = 0; i < 5; i++) {
      await page.keyboard.press('ArrowLeft');
    }
    await page.getByRole('button', { name: 'Apply' }).click();

    const cards = page.getByTestId('results-list').getByTestId('result-card');
    await expect(cards).toHaveCount(5);
  });

  test('filter changes review quality weight', async ({ page }) => {
    await page.getByPlaceholder('Search for a game...').fill('ELDEN RING');
    await expect(page.getByTestId('suggestions')).toBeVisible();
    await page.getByRole('listitem').first().click();
    await expect(page.getByTestId('results-list')).toBeVisible();
    const cards = page.getByTestId('results-list').getByTestId('result-card');
    await expect(cards).toHaveCount(10);

    const firstGameDefault = await cards.last().textContent();
    await page.getByRole('button', { name: '⚙' }).click();

    const qualitySlider = page.getByLabel('Review Quality Weight');
    await qualitySlider.focus();
    for (let i = 0; i < 40; i++) {
      await page.keyboard.press('ArrowRight');
    }
    await page.getByRole('button', { name: 'Apply' }).click();
    await expect(cards.last()).not.toHaveText(firstGameDefault as string);
  });

  test('go to game details page', async ({ page }) => {
    await page.getByPlaceholder('Search for a game...').fill('ELDEN RING');
    await expect(page.getByTestId('suggestions')).toBeVisible();
    await page.getByRole('listitem').first().click();

    await expect(page.getByTestId('results-list')).toBeVisible();
    const cards = page.getByTestId('results-list').getByTestId('result-card');
    await expect(cards).toHaveCount(10);

    await cards.first().click();

    await expect(page).toHaveURL(/\/games\/\d+/);
  });
});
