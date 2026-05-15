import { test, expect } from '@playwright/test';

test.describe('Profile', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/profile');
        await page.evaluate(() => localStorage.clear());
        await page.reload();
    });

    test('has title', async ({ page }) => {
        await expect(page).toHaveTitle("Grec");
    });

    test('has heading', async ({ page }) => {
        await expect(page.getByRole('heading', { name: 'My Game Profile' })).toBeVisible();
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

    test('shows suggestions when typing a game name', async ({ page }) => {
        await page.getByPlaceholder('Search for a game...').fill('ELDEN RING');
        await expect(page.getByTestId('suggestions')).toBeVisible();
    });

    test('shows empty state message when no games added', async ({ page }) => {
        await expect(page.getByText('Search and add games above to build your profile.')).toBeVisible();
    });

    test('add a game from suggestions', async ({ page }) => {
        await page.getByPlaceholder('Search for a game...').fill('ELDEN RING');
        await expect(page.getByTestId('suggestions')).toBeVisible();
        await page.getByRole('option').first().click();

        await expect(page.getByText('Games played')).toBeVisible();
        await expect(page.getByRole('link', { name: /elden ring/i })).toBeVisible();
    });

    test('remove a game from the list', async ({ page }) => {
        await page.getByPlaceholder('Search for a game...').fill('ELDEN RING');
        await expect(page.getByTestId('suggestions')).toBeVisible();
        await page.getByRole('option').first().click();
        await expect(page.getByRole('link', { name: /elden ring/i })).toBeVisible();

        await page.getByRole('button', { name: /Remove/i }).click();
        await expect(page.getByRole('link', { name: /elden ring/i })).not.toBeVisible();
    });

    test('edit hours for a game', async ({ page }) => {
        await page.getByPlaceholder('Search for a game...').fill('ELDEN RING');
        await expect(page.getByTestId('suggestions')).toBeVisible();
        await page.getByRole('option').first().click();

        const hoursInput = page.getByRole('spinbutton');
        await hoursInput.fill('42');
        await expect(hoursInput).toHaveValue('42');
    });

    test('shows Get Recommendations button after adding a game', async ({ page }) => {
        await page.getByPlaceholder('Search for a game...').fill('ELDEN RING');
        await expect(page.getByTestId('suggestions')).toBeVisible();
        await page.getByRole('option').first().click();

        await expect(page.getByRole('button', { name: 'Get Recommendations' })).toBeVisible();
    });

    test('empty state disappears after adding a game', async ({ page }) => {
        await expect(page.getByText('Search and add games above to build your profile.')).toBeVisible();

        await page.getByPlaceholder('Search for a game...').fill('ELDEN RING');
        await expect(page.getByTestId('suggestions')).toBeVisible();
        await page.getByRole('option').first().click();

        await expect(page.getByText('Search and add games above to build your profile.')).not.toBeVisible();
    });

    test('displays recommendations after clicking Get Recommendations', async ({ page }) => {
        await page.route('*/**/recommend/profile', async route => {
            await route.fulfill({
                json: {
                    recommendations: [
                        {
                            app_id: 123456,
                            game_name: 'Mocked Recommended Game',
                            header_image: '',
                            hybrid_score: 0.85,
                        },
                    ],
                },
            });
        });

        await page.getByPlaceholder('Search for a game...').fill('ELDEN RING');
        await expect(page.getByTestId('suggestions')).toBeVisible();
        await page.getByRole('option').first().click();

        await page.getByRole('button', { name: 'Get Recommendations' }).click();

        await expect(page.getByText('Recommended for you')).toBeVisible();
        await expect(page.getByText('Mocked Recommended Game')).toBeVisible();
        await expect(page.getByText('85.0%')).toBeVisible();
    });

    test('recommendation links navigate to game page', async ({ page }) => {
        await page.route('*/**/recommend/profile', async route => {
            await route.fulfill({
                json: {
                    recommendations: [
                        {
                            app_id: 123456,
                            game_name: 'Mocked Recommended Game',
                            header_image: '',
                            hybrid_score: 0.85,
                        },
                    ],
                },
            });
        });

        await page.getByPlaceholder('Search for a game...').fill('ELDEN RING');
        await expect(page.getByTestId('suggestions')).toBeVisible();
        await page.getByRole('option').first().click();
        await page.getByRole('button', { name: 'Get Recommendations' }).click();

        await expect(page.getByText('Mocked Recommended Game')).toBeVisible();
        await page.getByText('Mocked Recommended Game').click();
        await expect(page).toHaveURL('/games/123456');
    });
});
