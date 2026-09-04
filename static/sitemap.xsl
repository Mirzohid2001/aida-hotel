<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:s="http://www.sitemaps.org/schemas/sitemap/0.9"
  xmlns:xhtml="http://www.w3.org/1999/xhtml"
  exclude-result-prefixes="s xhtml">
  <xsl:output method="html" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">
    <html lang="en">
      <head>
        <meta charset="utf-8"/>
        <title>Aida Hotel — Sitemap</title>
        <style>
          body { font-family: system-ui, sans-serif; margin: 2rem; color: #1a1a1a; background: #fafafa; }
          h1 { font-size: 1.4rem; margin: 0 0 0.35rem; }
          p { color: #555; margin: 0 0 1.25rem; }
          table { border-collapse: collapse; width: 100%; background: #fff; }
          th, td { border: 1px solid #e5e5e5; padding: 0.55rem 0.7rem; text-align: left; font-size: 0.92rem; }
          th { background: #f0ebe3; }
          a { color: #8a6a3b; }
          .meta { white-space: nowrap; color: #666; }
        </style>
      </head>
      <body>
        <h1>Aida Hotel sitemap</h1>
        <p>This file is for search engines (Google, Yandex). URLs below are indexed for uz / ru / en.</p>
        <table>
          <thead>
            <tr>
              <th>URL</th>
              <th>Change frequency</th>
              <th>Priority</th>
            </tr>
          </thead>
          <tbody>
            <xsl:for-each select="s:urlset/s:url">
              <tr>
                <td><a href="{s:loc}"><xsl:value-of select="s:loc"/></a></td>
                <td class="meta"><xsl:value-of select="s:changefreq"/></td>
                <td class="meta"><xsl:value-of select="s:priority"/></td>
              </tr>
            </xsl:for-each>
          </tbody>
        </table>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
