# OSM OAuth 2.0 Reference

The following information summarizes the OSM OAuth 2.0 behaviour and endpoints.

## URLs

### Authorisation
`https://www.onlinescoutmanager.co.uk/oauth/authorize`

If you are using the 'authorization code flow', your client library will build a link based on this URL that your users will click - this will bring them to OSM where they will be asked to log in. If they log in and authorise your application, they will be redirected back to the Redirect URL you specify.

### Access token
`https://www.onlinescoutmanager.co.uk/oauth/token`

When the user has been redirected back to your application, your client library will make a request to this URL to get an 'access token' and a 'refresh token' - these should be stored in your database.

### Resource owner
`https://www.onlinescoutmanager.co.uk/oauth/resource`

This will provide you with the user's full name, email address, and a list of sections that your application can access.

## Scopes
Prefix each of the following scopes with `section:` and add the suffix of `:read` or `:write` to determine if your application needs read access (`:read`) or read and write access (`:write`).

The `administration` and `finance` scopes have an additional suffix of `:admin` which is used for editing critical settings.

Please ask for the lowest possible set of permissions as you will not be able to see sections unless the user has all the permissions your application specifies.

- `administration` - Administration / settings areas.
- `attendance` - Attendance Register
- `badge` - Badge records
- `event` - Events
- `finance` - Financial areas (online payments, invoices, etc)
- `flexirecord` - Flexi-records
- `member` - Personal details, including adding/removing/transferring, emailing, obtaining contact details etc.
- `programme` - Programme
- `quartermaster` - Quartermaster's area

## Using the API
Your browser uses a simple API for interacting with OSM, so although our API is unsupported and undocumented, your application will be able to do anything that you can do on the website.

You should use your browser's developer console to watch the network requests that are made when you perform the actions you would like your application to automate. Pay particular attention to whether requests are GET or POST. Then use your OAuth client library to create an authenticated request to the URL you discovered via the console (which will set a 'Bearer token' in the authorisation header).

## Rate limits
Please monitor the standard rate limit headers to ensure your application does not get blocked automatically. Applications that are frequently blocked will be permanently blocked.

- `X-RateLimit-Limit` - this is the number of requests per hour that your API can perform (per authenticated user)
- `X-RateLimit-Remaining` - this is the number of requests remaining that the current user can perform before they are blocked
- `X-RateLimit-Reset` - this is the number of seconds until the rate limit for the current user resets back to your overall limit

An HTTP 429 status code will be sent if the user goes over the limit, along with a `Retry-After` header with the number of seconds until you can use the API again.

Please also enforce your own lower rate limits, especially if you are allowing unauthenticated users to manipulate your data (e.g. allowing members to join a waiting list).

## Other considerations
Please ensure you check responses and abort if they are not as you expect - your application will get blocked if it frequently performs invalid requests.

Please monitor for a `X-Deprecated` header - anything with that header will be removed after the date mentioned.

Please monitor for a `X-Blocked` header - if this is set, your application has been blocked due to using invalid data or attempting to do something it does not have access to use. Continuing to use the API after you have been blocked will automatically change the block to a permanent block.

If you allow unauthenticated uses of your application, ensure you verify the users are not bots.

Always sanitise and validate data input before sending it to OSM - invalid data will result in your application being blocked.

