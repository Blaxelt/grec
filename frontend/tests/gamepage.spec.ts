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
    await expect(page.getByTestId('game-desc')).toBeVisible();
  });

  test('has game genres', async ({ page }) => {
    await expect(page.getByText(/Genres:/)).toBeVisible();
  });

  test('has game tags', async ({ page }) => {
    await expect(page.getByText(/Tags:/)).toBeVisible();
  });

  test('has screenshots section', async ({ page }) => {
    await expect(page.getByRole('heading', { level: 2, name: 'Screenshots' })).toBeVisible();
  });

  test('has other players also played section', async ({ page }) => {
    await page.route('*/**/games/570940', async route => {
      const request = route.request();

      // Only intercept API/fetch requests, not page navigation
      if (request.resourceType() !== 'fetch' && request.resourceType() !== 'xhr') {
        await route.continue();
        return;
      }

      const response = await route.fetch();
      const json = await response.json();

      json.other_players_also_played = [{
        app_id: 123456,
        game_name: 'Mocked Recommendation Game',
        header_image: '',
        hybrid_score: 0.99
      }];

      await route.fulfill({ json });
    });

    await page.goto('/games/570940');

    const playerLinks = page.getByTestId('recommendations').getByRole('link');

    await expect(playerLinks.first()).toBeVisible();
    await playerLinks.first().click();
    await expect(page).toHaveURL('/games/123456');
  });

  test('shows error for invalid game', async ({ page }) => {
    await page.goto('/games/99999999');
    await expect(page.getByText('Loading...')).toBeVisible();
  });
});
