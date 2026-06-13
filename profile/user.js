// MinaFox baseline prefs — copied into the custom profile.

// Firefox chrome CSS for the MinaFox hybrid UI.
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);

// Privacy / quiet startup
user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("browser.startup.page", 1);
user_pref("browser.startup.homepage", "__MINAFOX_START_URL__");

// Telemetry / Mozilla data reporting off.
// This disables collection/upload/reporting surfaces available at profile level.
user_pref("toolkit.telemetry.enabled", false);
user_pref("toolkit.telemetry.unified", false);
user_pref("toolkit.telemetry.server", "");
user_pref("toolkit.telemetry.archive.enabled", false);
user_pref("toolkit.telemetry.newProfilePing.enabled", false);
user_pref("toolkit.telemetry.shutdownPingSender.enabled", false);
user_pref("toolkit.telemetry.updatePing.enabled", false);
user_pref("toolkit.telemetry.bhrPing.enabled", false);
user_pref("toolkit.telemetry.firstShutdownPing.enabled", false);
user_pref("toolkit.telemetry.coverage.opt-out", true);
user_pref("toolkit.coverage.opt-out", true);
user_pref("toolkit.coverage.endpoint.base", "");

// Health report / data submission off.
user_pref("datareporting.healthreport.uploadEnabled", false);
user_pref("datareporting.healthreport.service.enabled", false);
user_pref("datareporting.policy.dataSubmissionEnabled", false);
user_pref("datareporting.policy.firstRunURL", "");
user_pref("datareporting.sessions.current.clean", true);

// Crash report checks and automatic submission off.
user_pref("browser.crashReports.unsubmittedCheck.enabled", false);
user_pref("browser.crashReports.unsubmittedCheck.autoSubmit2", false);
user_pref("browser.crashReports.unsubmittedCheck.autoSubmit", false);
user_pref("breakpad.reportURL", "");
user_pref("browser.tabs.crashReporting.sendReport", false);

// Studies, Shield, Normandy, experiments, and discovery off.
user_pref("app.shield.optoutstudies.enabled", false);
user_pref("app.normandy.enabled", false);
user_pref("app.normandy.api_url", "");
user_pref("messaging-system.rsexperimentloader.enabled", false);
user_pref("browser.discovery.enabled", false);

// New-tab / Activity Stream telemetry and sponsored content off.
user_pref("browser.newtabpage.activity-stream.telemetry", false);
user_pref("browser.newtabpage.activity-stream.feeds.telemetry", false);
user_pref("browser.newtabpage.activity-stream.showSponsored", false);
user_pref("browser.newtabpage.activity-stream.showSponsoredTopSites", false);
user_pref("browser.newtabpage.activity-stream.feeds.section.topstories", false);
user_pref("browser.newtabpage.activity-stream.feeds.snippets", false);

// Search/urlbar event telemetry and quick-suggest data collection off.
user_pref("browser.urlbar.eventTelemetry.enabled", false);
user_pref("browser.search.serpEventTelemetry.enabled", false);
user_pref("browser.search.serpEventTelemetryCategorization.enabled", false);
user_pref("browser.search.serpEventTelemetryCategorization.regionEnabled", false);
user_pref("browser.urlbar.quicksuggest.dataCollection.enabled", false);
user_pref("browser.urlbar.quicksuggest.enabled", false);

// Browser ping centre and background network probes off.
user_pref("browser.ping-centre.telemetry", false);
user_pref("network.captive-portal-service.enabled", false);
user_pref("network.connectivity-service.enabled", false);
user_pref("default-browser-agent.enabled", false);
user_pref("dom.private-attribution.submission.enabled", false);

// Keep Pocket off.
user_pref("extensions.pocket.enabled", false);

// Wayland / Hyprland friendliness
user_pref("widget.use-xdg-desktop-portal.file-picker", 1);
user_pref("widget.use-xdg-desktop-portal.mime-handler", 1);
user_pref("widget.use-xdg-desktop-portal.settings", 1);
user_pref("media.ffmpeg.vaapi.enabled", true);
user_pref("gfx.webrender.all", true);

// ADHD-friendly browsing defaults
user_pref("browser.tabs.warnOnClose", true);
user_pref("browser.tabs.warnOnCloseOtherTabs", true);
user_pref("browser.ctrlTab.sortByRecentlyUsed", true);
user_pref("findbar.highlightAll", true);
user_pref("layout.css.prefers-color-scheme.content-override", 0);

// Keep DRM possible for streaming; flip to false if you want stricter privacy.
user_pref("media.eme.enabled", true);
