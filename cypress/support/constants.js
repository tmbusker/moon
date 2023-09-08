export const COMMON_APP = 'cmm';

export const ADMIN_PATH = 'admin/';
export const AUTHGROUP_PATH = `${ADMIN_PATH}${COMMON_APP}/authgroup/`;
export const AUTHUSER_PATH = `${ADMIN_PATH}${COMMON_APP}/authuser/`;

export const BASE_URL = Cypress.config().baseUrl;
export const URL_ADMIN = `${BASE_URL}${ADMIN_PATH}`;
