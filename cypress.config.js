const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://127.0.0.1:8000/',
    "experimentalStudio": true,
    "video": false,
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
  },
});
