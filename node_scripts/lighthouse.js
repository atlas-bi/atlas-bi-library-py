async function login(browser) {
  console.log('open page');

  const page = await browser.newPage();
  await page.goto('http://127.0.0.1:8009');

  console.log('enter email');

  const emailInput = await page.$('input[name="username"]');
  if (emailInput) {
    await emailInput.type('admin@admin.admin');

    await Promise.all([page.$eval('form.box', (form) => form.submit())]);
  }
  // otherwise, we are already logged in.
  console.log('logged in');
  await page.close();
}

async function setup(browser) {
  await login(browser);
  console.log('starting lighthouse');
}

module.exports = setup;
