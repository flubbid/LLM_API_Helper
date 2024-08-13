const { test, expect } = require("@playwright/test");
const path = require("path");
const fs = require("fs");

const models = ["gpt-4-turbo", "gpt-3.5-turbo", "claude-3-sonnet-20240229"];
const testFilePath = path.join(__dirname, "gpt-test-doc.txt");

for (const model of models) {
  test(`Upload File Test for ${model}`, async ({ page }) => {
    await page.goto("http://localhost:5000");

    // Ensure the test file exists
    expect(fs.existsSync(testFilePath)).toBeTruthy();

    // Select the model
    await page.selectOption("#model-select", model);

    // Upload the file
    await page.setInputFiles("#file-upload", testFilePath);

    // Verify file upload
    // const fileListText = await page.textContent("#file-list");
    // expect(fileListText).toContain("gpt-test-doc.txt");

    // Enter the prompt
    await page.fill(
      "#user-input",
      'I have attached a file. This is a test to see if you are able to read the file. Respond with only the file\'s content, or respond with "no".'
    );

    // Submit the prompt
    await page.click("#send-btn");

    // Wait for and check the response
    const responseSelector = ".assistant-message:last-child";
    await page.waitForSelector(responseSelector, {
      state: "visible",
      timeout: 30000,
    });
    const response = await page.textContent(responseSelector);

    expect(response).not.toBe("no");
    expect(response).toContain("gpt-4-turbo - potato shmato - working --");

    // Clear chat for next test
    await page.click("#clear-history");
  });
}
