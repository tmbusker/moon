const constants = require('./constants');

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

Cypress.Commands.add('create_group', (group_name) => {
    const url_authgroup = `${constants.BASE_URL}${constants.AUTHGROUP_PATH}`;

    cy.get('tr.model-authgroup > th > a').click();
    // グループ一覧画面
    cy.url().should('eq', url_authgroup);
    const authgroup_add_path = `/${constants.AUTHGROUP_PATH}add/`;
    cy.get('#content-main a[href="' + authgroup_add_path + '"]').click();
    // グループ新規追加画面
    cy.get('#id_name').type(group_name);
    cy.get('#id_permissions_add_all_link').click();
    cy.get('input[type="submit"][name="_save"]').click();
    // グループ一覧画面
    cy.url().should('eq', url_authgroup);
});

Cypress.Commands.add('delete_group', (group) => {
    const url_authgroup = `${constants.BASE_URL}${constants.AUTHGROUP_PATH}`;

    cy.get('tr.model-authgroup > th > a').click();
    // グループ一覧画面
    cy.url().should('eq', url_authgroup);

    // グループ選択
    cy.contains('#content-main > #changelist #result_list a', group.name).click();

    // グループ継続編集画面
    cy.url().should(url => {
        const regexPattern = new RegExp(`${url_authgroup}\\d+/change/`);
        expect(url).to.match(regexPattern);
    });
    cy.get('div.submit-row > a.deletelink').click();
    // グループ削除確認画面
    cy.url().should(url => {
        const regexPattern = new RegExp(`${url_authgroup}\\d+/delete/`);
        expect(url).to.match(regexPattern);
    });
    cy.get('input[type="submit"]').click();

    // グループ一覧画面
    cy.url().should('eq', url_authgroup);
});

Cypress.Commands.add('create_user', (user) => {
    const url_authuser = `${constants.BASE_URL}${constants.AUTHUSER_PATH}`;

    cy.get('tr.model-authuser > th > a').click();
    // ユーザー一覧画面
    cy.url().should('eq', url_authuser);
    const authuser_add_path = `/${constants.AUTHUSER_PATH}add/`;
    cy.get('#content-main a[href="' + authuser_add_path + '"]').click();
    // ユーザー新規追加画面
    cy.get('#id_username').type(user.name);
    cy.get('#id_password1').type(user.password);
    cy.get('#id_password2').type(user.password);
    cy.get('input[type="submit"][name="_save"]').click();
    // ユーザー継続編集画面
    cy.url().should(url => {
        const regexPattern = new RegExp(`${url_authuser}\\d+/change/`);
        expect(url).to.match(regexPattern);
    });

    // ユーザー継続編集画面
    if (user.is_staff){
        cy.get('#id_is_staff').check();
    }
    if (user.is_superuser){
        cy.get('#id_is_superuser').check();
    }
    cy.get('#id_groups_from').select(user.group);
    cy.get('#id_groups_add_link').click();

    cy.get('input[type="submit"][name="_save"]').click();
    cy.url().should('eq', url_authuser);
});

Cypress.Commands.add('delete_user', (user) => {
    const url_authuser = `${constants.BASE_URL}${constants.AUTHUSER_PATH}`;

    cy.get('tr.model-authuser > th > a').click();
    // ユーザー一覧画面
    cy.url().should('eq', url_authuser);

    // ユーザー選択
    cy.contains('#content-main > #changelist #result_list a', user.name).click();

    // ユーザー継続編集画面
    cy.url().should(url => {
        const regexPattern = new RegExp(`${url_authuser}\\d+/change/`);
        expect(url).to.match(regexPattern);
    });
    cy.get('div.submit-row > a.deletelink').click();
    // ユーザー削除確認画面
    cy.url().should(url => {
        const regexPattern = new RegExp(`${url_authuser}\\d+/delete/`);
        expect(url).to.match(regexPattern);
    });
    cy.get('input[type="submit"]').click();
    // ユーザー一覧画面
    cy.url().should('eq', url_authuser);
});
