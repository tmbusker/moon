// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })
Cypress.Commands.add('login', (username) => {
    const fixture_file = `${username}.json`;
    cy.fixture(fixture_file).then((account) => {
        cy.visit('/')
        cy.get('#id_username').clear();
        cy.get('#id_username').type(account.username);
        cy.get('#id_password').clear();
        cy.get('#id_password').type(account.password);
        cy.get('.submit-row > input').click();
    });
});
