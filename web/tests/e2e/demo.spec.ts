import { expect, test } from "@playwright/test";

test("presenter can open the hero scenario from executive", async ({ page }) => {
  await page.goto("/executive");
  await expect(page.getByTestId("synthetic-badge")).toBeVisible();
  await page.getByTestId("open-hero").click();
  await expect(page.getByRole("heading", { name: "Monsoon flood + dengue surge" })).toBeVisible();
  await page.getByTestId("run-scenario").click();
  await expect(page.getByTestId("money-service")).toBeVisible({ timeout: 120_000 });
});
