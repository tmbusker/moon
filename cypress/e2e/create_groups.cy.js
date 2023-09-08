const constants = require('../support/constants');

describe('create groups', () => {
    beforeEach(() => {
        cy.login('admin');
        // 管理画面
        cy.url().should('eq', constants.URL_ADMIN);
        cy.get('tr.model-authgroup > th > a').should('have.attr', 'href', `/${constants.AUTHGROUP_PATH}`);
    })

    it('create_groups', () => {
        cy.fixture('groups.json').then((items) => {
            for (const item of items){
                cy.create_group(item.name);
            }
        })
    })
})