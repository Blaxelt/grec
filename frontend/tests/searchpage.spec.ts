import { test, expect } from '@playwright/test';

test.describe('Search Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/search');
  });

  test('has title', async ({ page }) => {
    await expect(page).toHaveTitle("Grec");
  });

  test('has heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Search' })).toBeVisible();
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
  });

  test('shows suggestions when typing a game name', async ({ page }) => {
    await page.getByPlaceholder('Search for a game...').fill('ELDEN RING');
    await expect(page.getByTestId('suggestions')).toBeVisible();
  });

  test('suggestions disappear when input is cleared', async ({ page }) => {
    const input = page.getByPlaceholder('Search for a game...');
    await input.fill('ELDEN RING');
    await expect(page.getByTestId('suggestions')).toBeVisible();

    await input.fill('');
    await expect(page.getByTestId('suggestions')).not.toBeVisible();
  });

  test('suggestions contain the searched game', async ({ page }) => {
    await page.getByPlaceholder('Search for a game...').fill('ELDEN RING');
    await expect(page.getByTestId('suggestions')).toBeVisible();

    await expect(page.getByTestId('suggestions').getByText(/^ELDEN RING$/)).toBeVisible();
  });

  test('no suggestions for nonexistent game', async ({ page }) => {
    await page.getByPlaceholder('Search for a game...').fill('Fallout 5');
    // wait for debounce + response
    await page.waitForTimeout(500);
    await expect(page.getByTestId('suggestions')).not.toBeVisible();
  });

  test('has navigation bar with links', async ({ page }) => {
    await expect(page.getByRole('navigation')).toBeVisible();
    await expect(page.getByRole('link', { name: 'Home' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Search' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Profile' })).toBeVisible();
  });

  test('has "or browse by tags" separator', async ({ page }) => {
    await expect(page.getByText('or browse by tags')).toBeVisible();
  });

  test('has tag search input', async ({ page }) => {
    await expect(page.getByPlaceholder(/Search for tags/)).toBeVisible();
  });

  test('tag search shows suggestions', async ({ page }) => {
    const tagInput = page.getByPlaceholder(/Search for tags/);
    await tagInput.fill('RPG');

    await expect(page.getByRole('listitem').filter({ hasText: /^RPG$/ })).toBeVisible();
  });

  test('selecting a tag adds a chip', async ({ page }) => {
    const tagInput = page.getByPlaceholder(/Search for tags/);
    await tagInput.fill('RPG');
    await page.getByRole('listitem').filter({ hasText: /^RPG$/ }).click();

    await expect(page.getByText('RPG').first()).toBeVisible();
    await expect(page.getByRole('button', { name: /Remove RPG/ })).toBeVisible();
  });

  test('removing a tag chip removes it', async ({ page }) => {
    const tagInput = page.getByPlaceholder(/Search for tags/);
    await tagInput.fill('RPG');
    await page.getByRole('listitem').filter({ hasText: /^RPG$/ }).click();
    await expect(page.getByRole('button', { name: /Remove RPG/ })).toBeVisible();

    await page.getByRole('button', { name: /Remove RPG/ }).click();
    await expect(page.getByRole('button', { name: /Remove RPG/ })).not.toBeVisible();
  });

  test('tag search shows game results', async ({ page }) => {
    const tagInput = page.getByPlaceholder(/Search for tags/);
    await tagInput.fill('RPG');
    await page.getByRole('listitem').filter({ hasText: /^RPG$/ }).click();

    // seed has Recommendation 0–11 with tag RPG → expect result cards
    await expect(page.getByTestId('result-card').first()).toBeVisible();
    await expect(page.getByText(/Showing \d+ game/)).toBeVisible();
  });

  test('clicking a tag result navigates to game page', async ({ page }) => {
    const tagInput = page.getByPlaceholder(/Search for tags/);
    await tagInput.fill('Action');
    await page.getByRole('listitem').filter({ hasText: /^Action$/ }).click();

    const card = page.getByTestId('result-card').first();
    await expect(card).toBeVisible();
    await card.click();

    await expect(page).toHaveURL(/\/games\/\d+/);
  });

  test('navigate to home via nav bar', async ({ page }) => {
    await page.getByRole('link', { name: 'Home' }).click();
    await expect(page).toHaveURL('/');
  });

  test('navigate to profile via nav bar', async ({ page }) => {
    await page.getByRole('link', { name: 'Profile' }).click();
    await expect(page).toHaveURL('/profile');
  });
});