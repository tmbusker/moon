import {COMMON_APP} from './constants';

describe('template spec', () => {
    const url_base = `${Cypress.config().baseUrl}`;
    const url_admin = 'admin/'
    const url_authgroup = url_admin + `${COMMON_APP}/authgroup/`;
    const url_authuser = url_admin + `${COMMON_APP}/authuser/`;

    beforeEach(() => {
        cy.login('admin');
        // 管理画面
        cy.url().should('eq', url_base + url_admin);
        cy.get('tr.model-authgroup > th > a').should('have.attr', 'href', '/' + url_authgroup);
    })

    it('add_group', () => {
        // 新規作成するグループの名前
        const group_name = `manager_${Math.floor(Math.random() * 10000)}`;

        cy.get('tr.model-authgroup > th > a').click();
        // グループ一覧画面
        cy.url().should('eq', url_base + url_authgroup);
        const url_authgroup_add = "/" + url_authgroup + "add/";
        cy.get('#content-main a[href="' + url_authgroup_add + '"]').click();
        // グループ新規追加画面
        cy.get('#id_name').type(group_name);
        cy.get('#id_permissions_add_all_link').click();
        cy.get('input[type="submit"][name="_save"]').click();
        // グループ一覧画面
        cy.url().should('eq', url_base + url_authgroup);
    })

    it('add_user', () => {
        // 新規作成するユーザーの名前
        const user_name = `user_${Math.floor(Math.random() * 10000)}`;
        const password = 'p09olp09ol';

        cy.get('tr.model-authuser > th > a').click();
        // ユーザー一覧画面
        cy.url().should('eq', url_base + url_authuser);
        const url_authuser_add = "/" + url_authuser + "add/";
        cy.get('#content-main a[href="' + url_authuser_add + '"]').click();
        // ユーザー新規追加画面
        cy.get('#id_username').type(user_name);
        cy.get('#id_password1').type(password);
        cy.get('#id_password2').type(password);
        cy.get('input[type="submit"][name="_save"]').click();
        // ユーザー継続編集画面
        cy.url().should(url => {
            const regexPattern = new RegExp(`${url_base + url_authuser}\\d+/change/`);
            expect(url).to.match(regexPattern);
        });
    })
})