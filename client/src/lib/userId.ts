const USER_ID_KEY = "chatToner_userId";
const COMPANY_ID_KEY = "chatToner_companyId";

/**
 * Retrieves the user ID from localStorage. If it doesn't exist,
 * generates a new UUID, stores it, and returns it.
 * @returns {string} The user's unique ID.
 */
export const getOrSetUserId = (): string => {
  let userId = localStorage.getItem(USER_ID_KEY);

  if (!userId) {
    userId = crypto.randomUUID();
    localStorage.setItem(USER_ID_KEY, userId);
  }

  return userId;
};

/**
 * Retrieves the company ID from localStorage. If it doesn't exist,
 * generates a new UUID, stores it, and returns it.
 * @returns {string} The unique company ID.
 */
export const getOrSetCompanyId = (): string => {
  let companyId = localStorage.getItem(COMPANY_ID_KEY);

  if (!companyId) {
    companyId = crypto.randomUUID();
    localStorage.setItem(COMPANY_ID_KEY, companyId);
  }

  return companyId;
};
