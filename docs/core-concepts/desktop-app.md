# Desktop app

Iris runs a desktop app that dynamically creates an `index.html` hub for navigating the registered dashboards. The app opens dashboards in a WebView, where the `IrisRuntimeSDK` can use the `webview` bridge to access their data.

The app has a settings modal with actions to:

- Manage the cache of each dashboard.
- Publish new partitions.
- Force publication of a specific dashboard's HTML without changing its published data.
- Republish the published `index.html` hub, for example after adding a dashboard that is not yet listed there.

The app's dynamically created navigation hub and the [published artifacts](publish-artifact.md) serve different environments. Republishing a dashboard's HTML or the published hub does not republish partition data.

The desktop app also runs [setup steps](setup-step.md) registered on the `Iris` object. They can show a status message and request fields needed by the configuration.
