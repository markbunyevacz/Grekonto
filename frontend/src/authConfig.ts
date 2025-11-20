export const msalConfig = {
  auth: {
    clientId: "ENTER_CLIENT_ID_HERE", // This should be replaced with the actual Client ID from Azure AD
    authority: "https://login.microsoftonline.com/common", // Or your tenant ID
    redirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: "sessionStorage", // This configures where your cache will be stored
    storeAuthStateInCookie: false, // Set this to "true" if you are having issues on IE11 or Edge
  },
};

export const loginRequest = {
  scopes: ["User.Read"],
};
