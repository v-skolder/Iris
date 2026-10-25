# Standalone Builder

Source dashboards may use separate HTML, CSS, JavaScript, images and other files under an `assets/` directory beside their HTML. The desktop app serves these source files directly. `StandaloneBuilder` transforms the source HTML into the single `<dash_id>.html` file saved in a publication environment. The web hub is also published as one `index.html` file. Partition payloads and manifests remain separate under `<dash_id>-data/`; "standalone" describes the dashboard presentation, not embedded data.

The builder uses Beautiful Soup to find local `href` and `src` references in the HTML. It embeds CSS and classic JavaScript into the HTML and converts local images to data URLs. It also resolves local `url(...)` references inside CSS. It preserves script execution order and timing when converting external scripts to inline code; unsupported loading modes fail with a clear error. A CSS or JavaScript dependency that cannot be embedded safely, including JavaScript module imports that require bundling, also stops publication. Asset paths must stay inside the source dashboard's `assets/` directory; the builder does not copy unrelated files or publish a separate assets folder.

The dashboard HTML loads `IrisRuntimeSDK` from its pinned CDN URL before its own scripts execute:

```html
<script src="https://cdn.jsdelivr.net/gh/v-skolder/Iris@v0.1.0/runtime/iris-runtime.js"></script>
```

The builder keeps this SDK script reference in the published HTML; it does not inline the SDK or publish a copy. The dashboard therefore needs access to that CDN at runtime. Other external CSS, JavaScript and image references must be embedded or rejected by the builder so local dashboard assets remain part of the one HTML file.

Publishing or force republishing dashboard HTML runs the builder again and replaces only that dashboard's HTML in the chosen environment. It does not rewrite partition payloads or `partitions.json`. The SHA-256 digest of the generated HTML in `publications.json` covers its embedded CSS, JavaScript, images and SDK URL, but not the remotely served SDK bytes. See [Published artifacts](publish-artifact.md) and [HTML Runtime](html-runtime.md).
