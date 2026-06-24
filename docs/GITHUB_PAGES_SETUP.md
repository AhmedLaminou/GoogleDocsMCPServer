# GitHub Pages and Google OAuth Branding Setup

This project includes a static site in `website/` for Google OAuth branding and
policy verification.

## Expected Public URLs

After GitHub Pages is enabled for this repository, the public URLs should be:

```text
https://ahmedlaminou.github.io/GoogleDocsMCPServer/
https://ahmedlaminou.github.io/GoogleDocsMCPServer/privacy/
https://ahmedlaminou.github.io/GoogleDocsMCPServer/terms/
```

Use the exact app name:

```text
AhmedLaminou Docs MCP
```

The Google OAuth consent screen app name must match the homepage name exactly.

## Enable GitHub Pages

1. Push the `website/` folder and `.github/workflows/pages.yml` to `main`.
2. Open the GitHub repository.
3. Go to **Settings -> Pages**.
4. Under **Build and deployment**, set **Source** to **GitHub Actions**.
5. Go to the **Actions** tab.
6. Run or wait for the **Pages** workflow.
7. Confirm the site opens at:

```text
https://ahmedlaminou.github.io/GoogleDocsMCPServer/
```

## Verify Ownership in Google Search Console

1. Open Google Search Console:

```text
https://search.google.com/search-console
```

2. Add a **URL-prefix property**:

```text
https://ahmedlaminou.github.io/GoogleDocsMCPServer/
```

3. Choose one of Google's verification methods.

If Google gives you an HTML verification file:

1. Download the file, for example `google1234567890abcdef.html`.
2. Put it directly in:

```text
website/google1234567890abcdef.html
```

3. Commit and push.
4. Wait for the Pages workflow to deploy.
5. Click **Verify** in Google Search Console.

If Google gives you an HTML meta tag:

1. Add that tag inside the `<head>` of `website/index.html`.
2. Commit and push.
3. Wait for the Pages workflow to deploy.
4. Click **Verify** in Google Search Console.

## Google OAuth Branding Values

In Google Cloud Console / Google Auth Platform, use:

App name:

```text
AhmedLaminou Docs MCP
```

Homepage:

```text
https://ahmedlaminou.github.io/GoogleDocsMCPServer/
```

Privacy policy:

```text
https://ahmedlaminou.github.io/GoogleDocsMCPServer/privacy/
```

Terms of service:

```text
https://ahmedlaminou.github.io/GoogleDocsMCPServer/terms/
```

Authorized domain:

```text
ahmedlaminou.github.io
```

## Notes

- Do not use the Git clone URL ending in `.git` as the homepage.
- Do not use GitHub `blob` URLs for privacy policy or terms in the OAuth
  consent screen.
- Do not use a Vercel or Render preview URL unless you can verify that exact
  domain or use a custom domain.
- The homepage must explain the app purpose and link to the privacy policy.
